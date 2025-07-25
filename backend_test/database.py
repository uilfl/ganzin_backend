#!/usr/bin/env python3
"""
Minimal PostgreSQL integration for Sol Glasses backend
Based on CLAUDE.md requirements for persistent gaze data storage
"""

import asyncio
import asyncpg
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

class GazeDatabase:
    """Minimal PostgreSQL database for gaze data storage"""
    
    def __init__(self, database_url: str = "postgresql://localhost:5432/sol_glasses"):
        self.database_url = database_url
        self.pool = None
    
    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(self.database_url, min_size=1, max_size=10)
            await self.create_tables()
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Database disconnected")
    
    async def create_tables(self):
        """Create required tables based on CLAUDE.md schema"""
        async with self.pool.acquire() as conn:
            # Raw samples table for bulk gaze data
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS raw_samples (
                    id SERIAL PRIMARY KEY,
                    timestamp BIGINT NOT NULL,
                    session_id VARCHAR(255) NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Index for performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_raw_samples_session_timestamp 
                ON raw_samples(session_id, timestamp);
            """)
            
            # Sessions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id VARCHAR(255) PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT NOW(),
                    ended_at TIMESTAMP,
                    sample_count INTEGER DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'active'
                );
            """)
            
            logger.info("Database tables created/verified")
    
    async def insert_gaze_sample(self, session_id: str, timestamp: int, gaze_data: dict, scene_data: Optional[str] = None):
        """Insert single gaze sample"""
        payload = {
            'gaze_data': gaze_data,
            'scene_data': scene_data,
            'received_at': datetime.utcnow().isoformat()
        }
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO raw_samples (timestamp, session_id, payload)
                VALUES ($1, $2, $3)
            """, timestamp, session_id, json.dumps(payload))
    
    async def bulk_insert_samples(self, samples: List[Dict[str, Any]]):
        """Bulk insert gaze samples for high performance"""
        if not samples:
            return
        
        records = [
            (sample['timestamp'], sample['session_id'], json.dumps({
                'gaze_data': sample['gaze_data'],
                'scene_data': sample.get('scene_data'),
                'received_at': sample.get('received_at', datetime.utcnow().isoformat())
            }))
            for sample in samples
        ]
        
        async with self.pool.acquire() as conn:
            await conn.executemany("""
                INSERT INTO raw_samples (timestamp, session_id, payload)
                VALUES ($1, $2, $3)
            """, records)
    
    async def create_session(self, session_id: str):
        """Create new session record"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO sessions (session_id) 
                VALUES ($1) 
                ON CONFLICT (session_id) DO NOTHING
            """, session_id)
    
    async def end_session(self, session_id: str, sample_count: int):
        """Mark session as ended"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE sessions 
                SET ended_at = NOW(), sample_count = $2, status = 'completed'
                WHERE session_id = $1
            """, session_id, sample_count)
    
    async def get_session_samples(self, session_id: str, limit: int = 100) -> List[dict]:
        """Get recent samples for a session"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT timestamp, payload, created_at
                FROM raw_samples 
                WHERE session_id = $1 
                ORDER BY timestamp DESC 
                LIMIT $2
            """, session_id, limit)
            
            return [
                {
                    'timestamp': row['timestamp'],
                    'created_at': row['created_at'].isoformat(),
                    **json.loads(row['payload'])
                }
                for row in rows
            ]
    
    async def get_active_sessions(self) -> List[dict]:
        """Get all active sessions"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT session_id, created_at, sample_count, status
                FROM sessions 
                WHERE status = 'active'
                ORDER BY created_at DESC
            """)
            
            return [dict(row) for row in rows]

# Global database instance
db = GazeDatabase()

async def init_database(database_url: str = None):
    """Initialize database connection"""
    if database_url:
        db.database_url = database_url
    await db.connect()

async def close_database():
    """Close database connection"""
    await db.disconnect()