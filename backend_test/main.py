#!/usr/bin/env python3
"""
Minimal Backend for Sol Glasses Integration Testing

This FastAPI server provides WebSocket endpoints to receive real-time gaze data
from Sol Glasses and store it for verification.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
# from database import db, init_database, close_database  # Disabled for now

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sol Glasses Backend Test",
    description="Minimal backend for testing Sol Glasses integration",
    version="1.0.0"
)

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session management
active_sessions: Dict[str, WebSocket] = {}
gaze_data_buffer: Dict[str, List[dict]] = {}  # Temporary buffer for batch inserts

# Global configuration
USE_DATABASE = False  # Set to True when PostgreSQL is available

class GazeSample(BaseModel):
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
    gaze_data: dict = Field(..., description="Gaze coordinates and confidence with x, y, confidence fields")
    scene_data: Optional[str] = Field(None, description="Base64 encoded scene image")

class SessionInfo(BaseModel):
    session_id: str
    connected_at: datetime
    sample_count: int
    last_sample_time: Optional[datetime]

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Sol Glasses Backend Test Server",
        "status": "running",
        "active_sessions": len(active_sessions),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """List all active sessions"""
    if USE_DATABASE and db.pool:
        # Get from database
        db_sessions = await db.get_active_sessions()
        return [
            SessionInfo(
                session_id=s['session_id'],
                connected_at=s['created_at'],
                sample_count=s['sample_count'],
                last_sample_time=s['created_at']
            )
            for s in db_sessions
        ]
    else:
        # In-memory fallback
        sessions = []
        for session_id, websocket in active_sessions.items():
            sample_count = len(gaze_data_buffer.get(session_id, []))
            sessions.append(SessionInfo(
                session_id=session_id,
                connected_at=datetime.utcnow(),
                sample_count=sample_count,
                last_sample_time=datetime.utcnow() if sample_count > 0 else None
            ))
        return sessions

@app.get("/sessions/{session_id}/samples")
async def get_session_samples(session_id: str, limit: int = 100):
    """Get recent gaze samples for a session"""
    if USE_DATABASE and db.pool:
        samples = await db.get_session_samples(session_id, limit)
        return {
            "session_id": session_id,
            "sample_count": len(samples),
            "samples": samples
        }
    else:
        # In-memory fallback
        if session_id not in gaze_data_buffer:
            raise HTTPException(status_code=404, detail="Session not found")
        
        samples = gaze_data_buffer[session_id][-limit:]
        return {
            "session_id": session_id,
            "sample_count": len(samples),
            "samples": samples
        }

@app.websocket("/ws/sessions/{session_id}")
async def gaze_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for receiving real-time gaze data from Sol Glasses
    
    Expected data format (based on Sol SDK):
    {
        "timestamp": 1642781234567,
        "gaze_data": {
            "x": 0.5,
            "y": 0.3,
            "confidence": 0.95
        },
        "scene_data": "base64_encoded_image_optional"
    }
    """
    await websocket.accept()
    active_sessions[session_id] = websocket
    gaze_data_buffer[session_id] = []
    
    # Create session in database
    if USE_DATABASE and db.pool:
        await db.create_session(session_id)
    
    logger.info(f"Session {session_id} connected")
    
    try:
        sample_count = 0
        start_time = time.time()
        
        while True:
            # Receive data from Sol Glasses
            data = await websocket.receive_text()
            
            try:
                # Parse incoming JSON data
                sample_data = json.loads(data)
                
                # Create gaze sample record
                gaze_sample = {
                    "timestamp": sample_data.get("timestamp", int(time.time() * 1000)),
                    "session_id": session_id,
                    "gaze_data": sample_data.get("gaze_data"),
                    "scene_data": sample_data.get("scene_data"),
                    "received_at": datetime.utcnow().isoformat(),
                    "sample_number": sample_count
                }
                
                # Store in buffer and database
                gaze_data_buffer[session_id].append(gaze_sample)
                sample_count += 1
                
                # Batch insert to database every 10 samples for performance
                if USE_DATABASE and db.pool and len(gaze_data_buffer[session_id]) >= 10:
                    try:
                        await db.bulk_insert_samples(gaze_data_buffer[session_id])
                        gaze_data_buffer[session_id].clear()  # Clear buffer after DB insert
                    except Exception as e:
                        logger.error(f"Database insert error: {e}")
                
                # Keep only last 100 samples in memory as fallback
                if len(gaze_data_buffer[session_id]) > 100:
                    gaze_data_buffer[session_id] = gaze_data_buffer[session_id][-100:]
                
                # Log performance stats every 100 samples
                if sample_count % 100 == 0:
                    elapsed = time.time() - start_time
                    hz = sample_count / elapsed
                    logger.info(f"Session {session_id}: {sample_count} samples, {hz:.1f} Hz")
                
                # Simple acknowledgment for high performance
                if sample_count % 50 == 0:  # Reduce echo frequency
                    await websocket.send_text(json.dumps({
                        "status": "batch_received",
                        "samples_processed": sample_count
                    }))
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from session {session_id}: {e}")
                await websocket.send_text(json.dumps({
                    "error": "Invalid JSON format",
                    "message": str(e)
                }))
            except Exception as e:
                logger.error(f"Error processing sample from session {session_id}: {e}")
                
    except WebSocketDisconnect:
        logger.info(f"Session {session_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        # Final database insert and cleanup
        final_count = sample_count
        if USE_DATABASE and db.pool:
            try:
                # Insert any remaining buffered samples
                if gaze_data_buffer.get(session_id):
                    await db.bulk_insert_samples(gaze_data_buffer[session_id]) 
                await db.end_session(session_id, final_count)
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
        
        # Cleanup
        if session_id in active_sessions:
            del active_sessions[session_id]
        if session_id in gaze_data_buffer:
            del gaze_data_buffer[session_id]
        
        logger.info(f"Session {session_id} ended with {final_count} samples")

@app.websocket("/ws/time-sync")
async def time_sync_websocket(websocket: WebSocket):
    """
    Time synchronization endpoint (matches Sol SDK time sync protocol)
    """
    await websocket.accept()
    logger.info("Time sync client connected")
    
    try:
        while True:
            # Receive binary time sync request
            data = await websocket.receive_bytes()
            
            # Sol SDK sends 8-byte timestamp, we echo it back with server time
            if len(data) == 8:
                import struct
                client_time = struct.unpack("!Q", data)[0]
                server_time = int(time.time() * 1000)  # Current server time in ms
                
                # Send back: client_time + server_time (16 bytes)
                response = struct.pack("!QQ", client_time, server_time)
                await websocket.send_bytes(response)
                
                logger.debug(f"Time sync: client={client_time}, server={server_time}")
            else:
                logger.warning(f"Invalid time sync request length: {len(data)}")
                
    except WebSocketDisconnect:
        logger.info("Time sync client disconnected")
    except Exception as e:
        logger.error(f"Time sync error: {e}")

# Calibration endpoint removed for minimal implementation

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    global USE_DATABASE
    if USE_DATABASE:
        try:
            await init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")
            logger.warning("Falling back to in-memory storage")
            USE_DATABASE = False

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections"""
    if USE_DATABASE and db.pool:
        await close_database()

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Sol Glasses Backend Test Server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )