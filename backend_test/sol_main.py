#!/usr/bin/env python3
"""
Sol Glasses Complete Backend
Implements all product requirements (R3-R9) with integrated services
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import our services
from sol_database import sol_db, init_sol_database, close_sol_database
from processing_service import get_processing_service, init_processing_service
from adaptation_service import get_adaptation_service, init_adaptation_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sol Glasses Complete Backend",
    description="Complete backend implementing all Sol Glasses requirements",
    version="2.0.0"
)

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global configuration
USE_DATABASE = False  # Set to True when PostgreSQL is available
USE_PROCESSING = True  # Enable processing and adaptation services

# Session management
active_sessions: Dict[str, WebSocket] = {}
gaze_data_buffer: Dict[str, List[dict]] = {}

class GazeSample(BaseModel):
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
    gaze_data: dict = Field(..., description="Gaze coordinates and confidence")
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
        "message": "Sol Glasses Complete Backend",
        "status": "running",
        "active_sessions": len(active_sessions),
        "services": {
            "database": USE_DATABASE,
            "processing": USE_PROCESSING,
            "adaptation": USE_PROCESSING
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """List all active sessions"""
    if USE_DATABASE and sol_db.pool:
        try:
            db_sessions = await sol_db.get_active_sessions()
            return [
                SessionInfo(
                    session_id=s['session_id'],
                    connected_at=s['created_at'],
                    sample_count=s['sample_count'],
                    last_sample_time=s['created_at']
                )
                for s in db_sessions
            ]
        except Exception as e:
            logger.error(f"Database error: {e}")
    
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
    if USE_DATABASE and sol_db.pool:
        try:
            samples = await sol_db.get_session_samples(session_id, limit)
            return {
                "session_id": session_id,
                "sample_count": len(samples),
                "samples": samples
            }
        except Exception as e:
            logger.error(f"Database error: {e}")
    
    # In-memory fallback
    if session_id not in gaze_data_buffer:
        raise HTTPException(status_code=404, detail="Session not found")
    
    samples = gaze_data_buffer[session_id][-limit:]
    return {
        "session_id": session_id,
        "sample_count": len(samples),
        "samples": samples
    }

@app.get("/sessions/{session_id}/revision")
async def get_revision_list(session_id: str):
    """R9: Get personalized revision list for session"""
    if USE_DATABASE and sol_db.pool:
        try:
            revision_list = await sol_db.generate_revision_list(session_id)
            return {
                "session_id": session_id,
                "revision_count": len(revision_list),
                "words": revision_list
            }
        except Exception as e:
            logger.error(f"Revision list error: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate revision list")
    else:
        raise HTTPException(status_code=503, detail="Database required for revision lists")

@app.get("/lessons/{lesson_id}/aois")
async def get_lesson_aois(lesson_id: str):
    """R2: Get AOI definitions for lesson rendering"""
    if USE_DATABASE and sol_db.pool:
        try:
            aois = await sol_db.get_aois_for_lesson(lesson_id)
            return {
                "lesson_id": lesson_id,
                "aoi_count": len(aois),
                "aois": aois
            }
        except Exception as e:
            logger.error(f"AOI retrieval error: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve AOIs")
    else:
        # Return mock AOIs for testing
        return {
            "lesson_id": lesson_id,
            "aoi_count": 3,
            "aois": [
                {"id": "word_1", "x": 100, "y": 50, "width": 80, "height": 20, "word_text": "example"},
                {"id": "word_2", "x": 200, "y": 50, "width": 60, "height": 20, "word_text": "text"},
                {"id": "sentence_1", "x": 100, "y": 80, "width": 300, "height": 40, "element_type": "sentence"}
            ]
        }

@app.websocket("/ws/sessions/{session_id}")
async def gaze_websocket(websocket: WebSocket, session_id: str):
    """
    R3-R5: Complete gaze data processing pipeline
    WebSocket endpoint for receiving real-time gaze data from Sol Glasses
    """
    await websocket.accept()
    active_sessions[session_id] = websocket
    gaze_data_buffer[session_id] = []
    
    # Create session in database
    if USE_DATABASE and sol_db.pool:
        try:
            await sol_db.create_session(session_id)
        except Exception as e:
            logger.error(f"Session creation error: {e}")
    
    # Register WebSocket for adaptive feedback (R5)
    if USE_PROCESSING:
        try:
            adaptation_service = get_adaptation_service()
            adaptation_service.register_websocket(session_id, websocket)
            
            # Initialize processing for session (assuming lesson_id from query params or default)
            processing_service = get_processing_service()
            if hasattr(processing_service, 'start_session_processing'):
                await processing_service.start_session_processing(session_id, "default_lesson")
        except Exception as e:
            logger.error(f"Processing initialization error: {e}")
    
    logger.info(f"Session {session_id} connected with full processing pipeline")
    
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
                
                # Store in buffer
                gaze_data_buffer[session_id].append(gaze_sample)
                sample_count += 1
                
                # R3: High-performance database ingestion with COPY
                if USE_DATABASE and sol_db.pool and len(gaze_data_buffer[session_id]) >= 10:
                    try:
                        await sol_db.bulk_insert_samples(gaze_data_buffer[session_id])
                        gaze_data_buffer[session_id].clear()
                    except Exception as e:
                        logger.error(f"Database insert error: {e}")
                
                # R4: Real-time processing and R5: adaptation feedback
                if USE_PROCESSING:
                    try:
                        # Process gaze sample for event detection
                        processing_service = get_processing_service()
                        events = await processing_service.process_gaze_sample(sample_data)
                        
                        # Trigger adaptive feedback for each detected event
                        adaptation_service = get_adaptation_service()
                        for event in events:
                            event_dict = {
                                'session_id': session_id,
                                'event_type': getattr(event, 'event_type', 'fixation'),
                                'duration_ms': getattr(event, 'duration_ms', 0),
                                'aoi_id': getattr(event, 'aoi_id', None)
                            }
                            feedback_commands = await adaptation_service.process_event(event_dict)
                            
                            # Log feedback for monitoring
                            if feedback_commands:
                                logger.info(f"Generated {len(feedback_commands)} feedback commands for session {session_id}")
                                
                    except Exception as e:
                        logger.error(f"Processing/adaptation error: {e}")
                
                # Keep memory usage manageable
                if len(gaze_data_buffer[session_id]) > 100:
                    gaze_data_buffer[session_id] = gaze_data_buffer[session_id][-100:]
                
                # Performance monitoring
                if sample_count % 100 == 0:
                    elapsed = time.time() - start_time
                    hz = sample_count / elapsed
                    logger.info(f"Session {session_id}: {sample_count} samples, {hz:.1f} Hz")
                
                # Acknowledgment (reduced frequency for performance)
                if sample_count % 50 == 0:
                    await websocket.send_text(json.dumps({
                        "status": "batch_processed",
                        "samples_processed": sample_count,
                        "processing_active": USE_PROCESSING
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
        # Session cleanup
        final_count = sample_count
        
        if USE_DATABASE and sol_db.pool:
            try:
                # Insert any remaining buffered samples
                if gaze_data_buffer.get(session_id):
                    await sol_db.bulk_insert_samples(gaze_data_buffer[session_id])
                
                # End session and generate revision list
                await sol_db.end_session(session_id, final_count)
                
                # R9: Generate personalized revision list
                revision_list = await sol_db.generate_revision_list(session_id)
                logger.info(f"Generated revision list with {len(revision_list)} items for session {session_id}")
                
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
        
        # Cleanup processing services
        if USE_PROCESSING:
            try:
                processing_service = get_processing_service()
                if hasattr(processing_service, 'end_session_processing'):
                    await processing_service.end_session_processing(session_id)
                
                adaptation_service = get_adaptation_service()
                adaptation_service.unregister_websocket(session_id)
            except Exception as e:
                logger.error(f"Processing cleanup error: {e}")
        
        # Memory cleanup
        if session_id in active_sessions:
            del active_sessions[session_id]
        if session_id in gaze_data_buffer:
            del gaze_data_buffer[session_id]
        
        logger.info(f"Session {session_id} ended with {final_count} samples")

@app.websocket("/ws/time-sync")
async def time_sync_websocket(websocket: WebSocket):
    """Time synchronization endpoint for Sol SDK"""
    await websocket.accept()
    logger.info("Time sync client connected")
    
    try:
        while True:
            data = await websocket.receive_bytes()
            
            if len(data) == 8:
                import struct
                client_time = struct.unpack("!Q", data)[0]
                server_time = int(time.time() * 1000)
                
                response = struct.pack("!QQ", client_time, server_time)
                await websocket.send_bytes(response)
                
                logger.debug(f"Time sync: client={client_time}, server={server_time}")
            else:
                logger.warning(f"Invalid time sync request length: {len(data)}")
                
    except WebSocketDisconnect:
        logger.info("Time sync client disconnected")
    except Exception as e:
        logger.error(f"Time sync error: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    global USE_DATABASE
    
    # Initialize database
    if USE_DATABASE:
        try:
            await init_sol_database()
            logger.info("Sol Glasses database initialized successfully")
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")
            logger.warning("Falling back to in-memory storage")
            USE_DATABASE = False
    
    # Initialize processing services
    if USE_PROCESSING:
        try:
            if USE_DATABASE and sol_db.pool:
                await init_processing_service(sol_db)
            await init_adaptation_service()
            logger.info("Processing and adaptation services initialized successfully")
        except Exception as e:
            logger.error(f"Processing services initialization failed: {e}")
    
    logger.info("Sol Glasses Complete Backend startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if USE_DATABASE and sol_db.pool:
        await close_sol_database()
    logger.info("Sol Glasses Complete Backend shutdown completed")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Sol Glasses Complete Backend...")
    uvicorn.run(
        "sol_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )