#!/usr/bin/env python3
"""
FastAPI Produc# Global managers (following project_structure.md pattern)
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

# Import our managers (following project_structure.md)
from manager.gaze_manager import GazeDataManager

# Setup logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="Sol Glasses Production Backend",
    description="Clean architecture backend integrating all testing insights",
    version="1.0.0"
)

# CORS for React frontend (from our testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global managers (following project_structure.md pattern)
gaze_manager = GazeDataManager()

@app.on_event("startup")
async def startup_event():
    """Initialize the system"""
    logger.info("=� Sol Glasses Production Backend Starting")
    logger.info("=� Integrated testing insights and clean architecture")
    logger.info("= Ready for frontend integration testing")

@app.on_event("shutdown") 
async def shutdown_event():
    """Clean shutdown"""
    logger.info("=� Shutting down Sol Glasses Backend")
    if gaze_manager.is_streaming:
        gaze_manager.stop_streaming_session()

# ==============================================================================
# CORE GAZE STREAMING ENDPOINTS (Based on our testing insights)
# ==============================================================================

@app.get("/api/status")
async def get_status():
    """
    Get comprehensive system status
    Based on frontend_integration_server_fixed.py insights
    """
    frontend_data = gaze_manager.get_frontend_data()
    session_stats = gaze_manager.get_session_statistics()
    
    return {
        "status": "running",
        "backend_version": "1.0.0_production",
        "architecture": "clean_modular",
        
        # Core streaming info
        "streaming": {
            "active": frontend_data["gaze"]["is_streaming"],
            "session_id": frontend_data["session"]["session_id"],  
            "total_samples": frontend_data["session"]["total_samples"],
            "duration": frontend_data["session"]["duration"]
        },
        
        # Session statistics
        "session_stats": session_stats,
        
        # System health
        "current_gaze": frontend_data["gaze"]["current"] is not None,
        "aoi_hits": frontend_data["aoi_hits"]["total_hits"],
        "timestamp": int(time.time() * 1000)
    }

@app.get("/api/gaze/stream")
async def stream_gaze_data(request: Request):
    """
    Server-Sent Events stream for real-time gaze data
    Based on frontend_integration_server_fixed.py pattern
    """
    
    async def event_stream():
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info("Client disconnected from gaze stream")
                    break
                
                # Get current data using our clean architecture
                data = gaze_manager.get_frontend_data()
                
                # Send as Server-Sent Event
                yield f"data: {json.dumps(data)}\n\n"
                
                # 20Hz update rate (from our testing insights)
                await asyncio.sleep(0.05)
                
        except asyncio.CancelledError:
            logger.info("SSE stream cancelled")
        except Exception as e:
            logger.error(f"SSE stream error: {e}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive", 
            "Content-Type": "text/event-stream",
        }
    )

@app.get("/api/gaze/current")
async def get_current_gaze():
    """Get current gaze point for polling-based clients"""
    return gaze_manager.get_frontend_data()

# ==============================================================================
# SESSION MANAGEMENT ENDPOINTS (From our testing insights)
# ==============================================================================

@app.post("/api/session/start")
async def start_session(session_data: dict):
    """
    Start new learning session
    Based on LearningSession.tsx integration testing
    """
    session_id = session_data.get("sessionId", f"session_{int(time.time())}")
    student_name = session_data.get("studentName", "Unknown Student")
    lesson_title = session_data.get("lessonTitle", "Interactive Reading")
    
    logger.info(f"=� Starting session: {session_id} for {student_name}")
    
    success = gaze_manager.start_streaming_session(session_id)
    
    if success:
        return {
            "status": "success",
            "session_id": session_id,
            "student_name": student_name,
            "lesson_title": lesson_title,
            "message": f"Started session for {student_name}",
            "timestamp": int(time.time() * 1000)
        }
    else:
        return {
            "status": "error", 
            "message": "Failed to start streaming session",
            "timestamp": int(time.time() * 1000)
        }

@app.post("/api/session/stop")
async def stop_session(session_data: dict):
    """
    Stop session and export data
    Based on our JSON persistence testing
    """
    session_id = session_data.get("sessionId")
    
    if not session_id:
        return {"status": "error", "message": "Session ID required"}
    
    logger.info(f"=� Stopping session: {session_id}")
    
    # Get final statistics before stopping
    final_stats = gaze_manager.get_session_statistics()
    
    # Stop session and get export filename
    filename = gaze_manager.stop_streaming_session()
    
    if filename:
        return {
            "status": "success",
            "session_id": session_id,
            "filename": filename,
            "final_statistics": final_stats,
            "message": f"Session data exported to {filename}",
            "timestamp": int(time.time() * 1000)
        }
    else:
        return {
            "status": "error",
            "message": "Failed to export session data",
            "timestamp": int(time.time() * 1000)
        }

@app.get("/api/session/statistics")
async def get_session_statistics():
    """Get real-time session statistics"""
    return gaze_manager.get_session_statistics()

# ==============================================================================
# AOI MANAGEMENT ENDPOINTS (Based on vocabulary discovery testing)
# ==============================================================================

@app.get("/api/aoi/list")
async def get_aoi_list():
    """Get all current AOI elements"""
    frontend_data = gaze_manager.get_frontend_data()
    return {
        "aois": frontend_data["aois"],
        "total_count": len(frontend_data["aois"]),
        "timestamp": int(time.time() * 1000)
    }

@app.post("/api/aoi/add")
async def add_dynamic_aoi(aoi_data: dict):
    """
    Add dynamic AOI element
    Supporting frontend dynamic content updates
    """
    success = gaze_manager.add_dynamic_aoi(aoi_data)
    
    if success:
        return {
            "status": "success",
            "aoi_id": aoi_data.get("id", "unknown"),
            "message": "AOI added successfully"
        }
    else:
        return {
            "status": "error",
            "message": "Failed to add AOI"
        }

@app.get("/api/aoi/hits")
async def get_recent_aoi_hits():
    """Get recent AOI hits for analysis"""
    frontend_data = gaze_manager.get_frontend_data()
    return {
        "recent_hits": frontend_data["aoi_hits"]["recent"],
        "total_hits": frontend_data["aoi_hits"]["total_hits"],
        "timestamp": int(time.time() * 1000)
    }

# ==============================================================================
# HEALTH AND MONITORING ENDPOINTS  
# ==============================================================================

@app.get("/api/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "service": "sol_glasses_backend",
        "version": "1.0.0_production",
        "timestamp": int(time.time() * 1000)
    }

@app.get("/api/performance")
async def get_performance_metrics():
    """Get system performance metrics"""
    frontend_data = gaze_manager.get_frontend_data()
    
    return {
        "gaze_streaming": {
            "active": frontend_data["gaze"]["is_streaming"],
            "samples_collected": frontend_data["session"]["total_samples"],
            "session_duration": frontend_data["session"]["duration"],
            "samples_per_second": (
                frontend_data["session"]["total_samples"] / max(frontend_data["session"]["duration"], 1) 
                if frontend_data["session"]["duration"] > 0 else 0
            )
        },
        "aoi_processing": {
            "total_hits": frontend_data["aoi_hits"]["total_hits"],
            "aoi_count": len(frontend_data["aois"])
        },
        "system": {
            "calibrated": frontend_data["calibration"]["calibrated"],
            "accuracy_px": frontend_data["calibration"]["accuracy_px"]
        },
        "timestamp": int(time.time() * 1000)
    }

# ==============================================================================
# TEXT-COORDINATE MAPPING ENDPOINTS (For testing our approach)
# ==============================================================================

@app.post("/api/text/upload")
async def upload_text_for_mapping(request: Request):
    """
    Upload text content for coordinate mapping testing
    Supports our LLM-based vocabulary tagging approach
    """
    try:
        body = await request.json()
        text_content = body.get("content", "")
        title = body.get("title", "Untitled")
        vocabulary_tags = body.get("vocabulary_tags", [])
        
        # Store the text content in gaze manager for AOI creation
        text_id = f"text_{int(time.time())}"
        success = gaze_manager.set_text_content(text_id, text_content, vocabulary_tags)
        
        if success:
            return {
                "status": "success",
                "text_id": text_id,
                "title": title,
                "vocabulary_count": len(vocabulary_tags),
                "message": "Text uploaded and ready for coordinate mapping"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to process text content"
            }
            
    except Exception as e:
        logger.error(f"Text upload error: {e}")
        return {
            "status": "error", 
            "message": f"Upload failed: {str(e)}"
        }

@app.post("/api/text/create-aois")
async def create_aois_from_coordinates(aoi_data: dict):
    """
    Create AOIs from frontend coordinate mapping
    This is called after text-coordinate mapping is complete
    """
    try:
        text_id = aoi_data.get("text_id")
        coordinates = aoi_data.get("coordinates", [])  # Format: [{"word": "...", "bbox": [x,y,w,h]}, ...]
        
        success_count = 0
        for coord in coordinates:
            word = coord.get("word", "")
            bbox = coord.get("bbox", [0, 0, 0, 0])
            
            aoi_success = gaze_manager.add_text_aoi(
                word_id=f"{text_id}_{word}",
                word=word,
                x=bbox[0],
                y=bbox[1], 
                width=bbox[2],
                height=bbox[3]
            )
            
            if aoi_success:
                success_count += 1
        
        return {
            "status": "success",
            "text_id": text_id,
            "aois_created": success_count,
            "total_coordinates": len(coordinates),
            "message": f"Created {success_count} AOIs for vocabulary tracking"
        }
        
    except Exception as e:
        logger.error(f"AOI creation error: {e}")
        return {
            "status": "error",
            "message": f"AOI creation failed: {str(e)}"
        }

@app.get("/api/text/vocabulary-hits")
async def get_vocabulary_hits():
    """
    Get real-time vocabulary hits from gaze data
    Perfect for testing our 800ms fixation detection
    """
    frontend_data = gaze_manager.get_frontend_data()
    
    # Filter for vocabulary-specific hits
    vocab_hits = []
    for hit in frontend_data["aoi_hits"]["recent"]:
        if hit.get("type") == "vocabulary" or "word" in hit.get("aoi_id", ""):
            vocab_hits.append({
                "word": hit.get("word", hit.get("aoi_id", "").replace("_", " ")),
                "timestamp": hit.get("timestamp", 0),
                "gaze_x": hit.get("gaze_x", 0),
                "gaze_y": hit.get("gaze_y", 0),
                "fixation_duration": hit.get("fixation_duration", 0),
                "confidence": hit.get("confidence", 0)
            })
    
    return {
        "vocabulary_hits": vocab_hits,
        "total_vocabulary_hits": len(vocab_hits),
        "timestamp": int(time.time() * 1000)
    }

@app.post("/api/llm/define-vocabulary")
async def get_vocabulary_definition(request: Request):
    """
    Stage 2 LLM: Get vocabulary definition when student needs help
    Called when 800ms+ fixation is detected on vocabulary
    """
    try:
        body = await request.json()
        word = body.get("word", "")
        context = body.get("context", "")
        user_profile = body.get("user_profile", {})
        
        # For now, mock the LLM response (replace with actual LLM API call)
        definition_response = {
            "word": word,
            "definition": f"A comprehensive definition of '{word}' tailored for {user_profile.get('level', 'intermediate')} level students.",
            "simplified_definition": f"Simple explanation: {word} means...",
            "example_sentence": f"Here's how to use {word} in a sentence.",
            "part_of_speech": "noun",  # Would be determined by LLM
            # no difficulty_explanation here neccessarily, checking our other places parsing this as well.
            "difficulty_explanation": f"This word might be challenging because...",
            "learning_tip": "Memory aid or learning strategy here",
            "synonyms": ["similar", "related", "equivalent"],
            "response_time": int(time.time() * 1000)
        }
        
        logger.info(f"📚 LLM Stage 2: Provided definition for '{word}'")
        
        return definition_response
        
    except Exception as e:
        logger.error(f"LLM definition error: {e}")
        return {
            "error": f"Failed to get definition: {str(e)}"
        }

# ==============================================================================
# DEVELOPMENT AND DEBUG ENDPOINTS (For frontend testing)
# ==============================================================================

@app.get("/api/debug/info")
async def get_debug_info():
    """Get comprehensive debug information for development"""
    return {
        "backend_architecture": "clean_modular_production",
        "components": {
            "gaze_manager": "GazeDataManager with official Sol SDK integration",
            "aoi_system": "AOICollection with vocabulary discovery",
            "hit_logging": "HitLogManager with session persistence",  
            "export_system": "JSON export following project_structure.md"
        },
        "testing_insights_integrated": [
            "Calibration coordinate transformation",
            "Vocabulary discovery AOI mapping", 
            "Real-time frontend data streaming",
            "Session JSON persistence",
            "Performance optimization (20Hz streaming)"
        ],
        "ready_for_frontend_testing": True,
        "timestamp": int(time.time() * 1000)
    }

# ==============================================================================
# MAIN APPLICATION RUNNER
# ==============================================================================

if __name__ == "__main__":
    print("=� Sol Glasses Production Backend Server")
    print("<�  Clean Architecture with Testing Insights")
    print("=� Port: 8000 (production)")
    print("= Frontend Integration Ready")
    print("=� Endpoints:")
    print("  Status: http://localhost:8000/api/status")
    print("  Stream: http://localhost:8000/api/gaze/stream")
    print("  Health: http://localhost:8000/api/health")
    print("  Debug: http://localhost:8000/api/debug/info")
    print("=� Press Ctrl+C to stop")
    print("-" * 60)
    
    # Run the production server
    uvicorn.run(
        "app:app",
        host="localhost",
        port=8000,
        log_level="info",
        reload=False  # Production mode
    )