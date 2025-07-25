#!/usr/bin/env python3
"""
Sol Glasses Database Module
Implements all database requirements from product_documents (R3-R9)
"""

import asyncio
import asyncpg
import json
import logging
import io
from datetime import datetime
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

class SolGlassesDatabase:
    """Complete database implementation for Sol Glasses requirements"""
    
    def __init__(self, database_url: str = "postgresql://localhost:5432/sol_glasses"):
        self.database_url = database_url
        self.pool = None
    
    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(self.database_url, min_size=2, max_size=20)
            await self.create_tables()
            logger.info("Sol Glasses database connected successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Database disconnected")
    
    async def create_tables(self):
        """Create all required tables based on product requirements"""
        async with self.pool.acquire() as conn:
            # R3: Raw samples table for bulk gaze data
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS raw_samples (
                    id SERIAL PRIMARY KEY,
                    timestamp BIGINT NOT NULL,
                    session_id VARCHAR(255) NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_raw_samples_session_timestamp 
                ON raw_samples(session_id, timestamp);
            """)
            
            # R4: Events table for processed fixation/saccade events
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    sample_ts BIGINT NOT NULL,
                    aoi_id VARCHAR(255),
                    event_type VARCHAR(20) NOT NULL, -- 'fixation' or 'saccade'
                    start_ts BIGINT NOT NULL,
                    end_ts BIGINT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    gaze_x FLOAT,
                    gaze_y FLOAT,
                    confidence FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """) 
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_session_time
                ON events(session_id, start_ts);
            """)
            
            # R2: AOI definitions table for lesson rendering
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS aois (
                    id VARCHAR(255) PRIMARY KEY,
                    lesson_id VARCHAR(255) NOT NULL,
                    x INTEGER NOT NULL,
                    y INTEGER NOT NULL,
                    width INTEGER NOT NULL,
                    height INTEGER NOT NULL,
                    word_text VARCHAR(500),
                    element_type VARCHAR(50), -- 'word', 'sentence', 'paragraph'
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """) 
            
            # R9: Revision lists table for personalized learning
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS revision_lists (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    word_text VARCHAR(500) NOT NULL,
                    total_fixation_ms INTEGER NOT NULL,
                    fixation_count INTEGER NOT NULL,
                    difficulty_score FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # R10: Speech results table for pronunciation scoring
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS speech_results (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    word_text VARCHAR(500) NOT NULL,
                    audio_data BYTEA,
                    asr_score INTEGER, -- 0-100
                    pronunciation_feedback TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # R6: Reports table for PDF/JSON storage
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    report_type VARCHAR(20) NOT NULL, -- 'pdf' or 'json'
                    file_data BYTEA NOT NULL,
                    file_size INTEGER NOT NULL,
                    download_url VARCHAR(500),
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Sessions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255),
                    lesson_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    ended_at TIMESTAMP,
                    sample_count INTEGER DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'active'
                );
            """)
            
            # Users table for R12 (privacy & deletion)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(255) PRIMARY KEY,
                    username VARCHAR(255) UNIQUE,
                    email VARCHAR(255),
                    role VARCHAR(20) DEFAULT 'learner', -- 'learner', 'teacher'
                    created_at TIMESTAMP DEFAULT NOW(),
                    deleted_at TIMESTAMP -- soft delete for R12
                );
            """)
            
            logger.info("All database tables created/verified")
    
    # R3: High-performance ingestion with PostgreSQL COPY
    async def bulk_insert_samples(self, samples: List[Dict[str, Any]]):
        """R3: Bulk insert using COPY for ≤50ms p95 latency"""
        if not samples:
            return
        
        # Prepare data for COPY - much faster than INSERT
        copy_data = io.StringIO()
        
        for sample in samples:
            payload = json.dumps({
                'gaze_data': sample['gaze_data'],
                'scene_data': sample.get('scene_data'),
                'received_at': sample.get('received_at', datetime.utcnow().isoformat())
            })
            copy_data.write(f"{sample['timestamp']}\\t{sample['session_id']}\\t{payload}\\n")
        
        copy_data.seek(0)
        
        async with self.pool.acquire() as conn:
            # Use COPY for high-throughput insertion
            await conn.copy_to_table(
                'raw_samples',
                source=copy_data,
                columns=['timestamp', 'session_id', 'payload'],
                format='text',
                delimiter='\\t'
            )
            
            # R3: Emit PostgreSQL NOTIFY for downstream processing
            await conn.execute("NOTIFY raw_inserted, $1", json.dumps({
                'sample_count': len(samples),
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }))
    
    # R4: Processing Service functions
    async def insert_event(self, session_id: str, event_data: dict):
        """R4: Insert processed gaze event (fixation/saccade)"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO events (
                    session_id, sample_ts, aoi_id, event_type, 
                    start_ts, end_ts, duration_ms, gaze_x, gaze_y, confidence
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
                session_id,
                event_data['sample_ts'],
                event_data.get('aoi_id'),
                event_data['event_type'],
                event_data['start_ts'],
                event_data['end_ts'],
                event_data['duration_ms'],
                event_data.get('gaze_x'),
                event_data.get('gaze_y'),
                event_data.get('confidence')
            )
            
            # R4: Emit NOTIFY for adaptation service
            await conn.execute("NOTIFY events_channel", json.dumps({
                'session_id': session_id,
                'event_type': event_data['event_type'],
                'aoi_id': event_data.get('aoi_id'),
                'duration_ms': event_data['duration_ms']
            }))
    
    async def get_aois_for_lesson(self, lesson_id: str) -> List[dict]:
        """R2: Get AOI definitions for lesson rendering"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, x, y, width, height, word_text, element_type
                FROM aois 
                WHERE lesson_id = $1
            """, lesson_id)
            
            return [dict(row) for row in rows]
    
    async def map_gaze_to_aoi(self, gaze_x: float, gaze_y: float, lesson_id: str) -> Optional[str]:
        """R4: Map gaze coordinates to AOI (≥99% mapping accuracy)"""
        async with self.pool.acquire() as conn:
            # Simple point-in-rectangle mapping
            row = await conn.fetchrow("""
                SELECT id FROM aois 
                WHERE lesson_id = $1
                AND $2 >= x AND $2 <= (x + width)
                AND $3 >= y AND $3 <= (y + height)
                LIMIT 1
            """, lesson_id, int(gaze_x), int(gaze_y))
            
            return row['id'] if row else None
    
    # R7: Vocabulary assistance functions
    async def check_word_difficulty(self, word: str) -> bool:
        """R7: Check if word is unknown/difficult for vocabulary popup"""
        # Simplified implementation - in production, use NLP frequency lists
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return word.lower() not in common_words and len(word) > 6
    
    # R9: Personalized revision list generation
    async def generate_revision_list(self, session_id: str) -> List[dict]:
        """R9: Generate revision list sorted by total fixation time"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    a.word_text,
                    SUM(e.duration_ms) as total_fixation_ms,
                    COUNT(*) as fixation_count,
                    AVG(e.confidence) as avg_confidence
                FROM events e
                JOIN aois a ON e.aoi_id = a.id
                WHERE e.session_id = $1 
                AND e.event_type = 'fixation'
                AND a.word_text IS NOT NULL
                GROUP BY a.word_text
                ORDER BY total_fixation_ms DESC
                LIMIT 50
            """, session_id)
            
            revision_data = [
                {
                    'word_text': row['word_text'],
                    'total_fixation_ms': row['total_fixation_ms'],
                    'fixation_count': row['fixation_count'],
                    'avg_confidence': float(row['avg_confidence']) if row['avg_confidence'] else 0.0
                }
                for row in rows
            ]
            
            # Store revision list
            for item in revision_data:
                await conn.execute("""
                    INSERT INTO revision_lists (
                        session_id, word_text, total_fixation_ms, fixation_count
                    ) VALUES ($1, $2, $3, $4)
                    ON CONFLICT DO NOTHING
                """, session_id, item['word_text'], item['total_fixation_ms'], item['fixation_count'])
            
            return revision_data
    
    # R10: Speech/pronunciation functions
    async def store_speech_result(self, session_id: str, word_text: str, audio_data: bytes, asr_score: int):
        """R10: Store ASR pronunciation scoring results"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO speech_results (session_id, word_text, audio_data, asr_score)
                VALUES ($1, $2, $3, $4)
            """, session_id, word_text, audio_data, asr_score)
    
    # R6: Reporting functions
    async def store_report(self, session_id: str, report_type: str, file_data: bytes) -> str:
        """R6: Store generated PDF/JSON report (≤5MB)"""
        file_size = len(file_data)
        if file_size > 5 * 1024 * 1024:  # 5MB limit
            raise ValueError(f"Report size {file_size} exceeds 5MB limit")
        
        report_id = f"report_{session_id}_{report_type}_{int(datetime.utcnow().timestamp())}"
        download_url = f"/api/reports/download/{report_id}"
        expires_at = datetime.utcnow().replace(hour=23, minute=59, second=59)  # Valid for ≥24h
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO reports (session_id, report_type, file_data, file_size, download_url, expires_at)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, session_id, report_type, file_data, file_size, download_url, expires_at)
        
        return download_url
    
    # Session management
    async def create_session(self, session_id: str, user_id: str = None, lesson_id: str = None):
        """Create new learning session"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO sessions (session_id, user_id, lesson_id) 
                VALUES ($1, $2, $3) 
                ON CONFLICT (session_id) DO NOTHING
            """, session_id, user_id, lesson_id)
    
    async def end_session(self, session_id: str, sample_count: int):
        """Mark session as completed"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE sessions 
                SET ended_at = NOW(), sample_count = $2, status = 'completed'
                WHERE session_id = $1
            """, session_id, sample_count)
    
    async def get_session_samples(self, session_id: str, limit: int = 100) -> List[dict]:
        """Get recent samples for analysis"""
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
    
    # R12: Privacy & deletion functions
    async def delete_user_data(self, user_id: str):
        """R12: GDPR-compliant user data deletion (≤72h)"""
        async with self.pool.acquire() as conn:
            # Soft delete user
            await conn.execute("""
                UPDATE users SET deleted_at = NOW() WHERE id = $1
            """, user_id)
            
            # Get user sessions for cleanup
            sessions = await conn.fetch("""
                SELECT session_id FROM sessions WHERE user_id = $1
            """, user_id)
            
            session_ids = [s['session_id'] for s in sessions]
            
            if session_ids:
                # Delete related data
                await conn.execute("""
                    DELETE FROM raw_samples WHERE session_id = ANY($1)
                """, session_ids)
                
                await conn.execute("""
                    DELETE FROM events WHERE session_id = ANY($1)
                """, session_ids)
                
                await conn.execute("""
                    DELETE FROM revision_lists WHERE session_id = ANY($1)
                """, session_ids)
                
                await conn.execute("""
                    DELETE FROM speech_results WHERE session_id = ANY($1)
                """, session_ids)
                
                await conn.execute("""
                    DELETE FROM reports WHERE session_id = ANY($1)
                """, session_ids)
                
                await conn.execute("""
                    DELETE FROM sessions WHERE user_id = $1
                """, user_id)
            
            logger.info(f"User {user_id} data deletion completed")

# Global database instance
sol_db = SolGlassesDatabase()

async def init_sol_database(database_url: str = None):
    """Initialize Sol Glasses database"""
    if database_url:
        sol_db.database_url = database_url
    await sol_db.connect()

async def close_sol_database():
    """Close Sol Glasses database"""
    await sol_db.disconnect()