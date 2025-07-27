#!/usr/bin/env python3
"""
FastAPI Production Backend Server
Integrates all testing insights with clean architecture
Following project_structure.md guidance for frontend integration
"""

import asyncio
import json
import time
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
        
        # Calibration status (from our testing)
        "calibration": {
            "calibrated": frontend_data["calibration"]["calibrated"],
            "accuracy_px": frontend_data["calibration"]["accuracy_px"]
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
# CALIBRATION ENDPOINTS (Based on your decision: 前端 UI 流程控制、後端負責計算轉換與保存參數)
# ==============================================================================

@app.post("/api/calibration/start")
async def start_calibration():
    """Start calibration process"""
    logger.info("🎯 Starting calibration process")
    
    # Reset calibration state
    success = gaze_manager.start_calibration_process()
    
    if success:
        return {
            "status": "success",
            "message": "Calibration process started",
            "points_required": 9,
            "timestamp": int(time.time() * 1000)
        }
    else:
        return {
            "status": "error",
            "message": "Failed to start calibration process",
            "timestamp": int(time.time() * 1000)
        }

@app.post("/api/calibration/capture_point")
async def capture_calibration_point(point_data: dict):
    """
    Capture calibration point
    Frontend sends: {point_index, screen_x, screen_y}
    Backend captures gaze and stores sample
    """
    point_index = point_data.get("point_index", 0)
    screen_x = point_data.get("screen_x", 0)
    screen_y = point_data.get("screen_y", 0)
    
    logger.info(f"📍 Capturing calibration point {point_index} at ({screen_x}, {screen_y})")
    
    # Capture current gaze point
    success, gaze_data = gaze_manager.capture_calibration_point(point_index, screen_x, screen_y)
    
    if success:
        return {
            "status": "success",
            "point_index": point_index,
            "gaze_captured": gaze_data,
            "message": f"Point {point_index} captured successfully",
            "timestamp": int(time.time() * 1000)
        }
    else:
        return {
            "status": "error",
            "message": f"Failed to capture point {point_index}",
            "timestamp": int(time.time() * 1000)
        }

@app.post("/api/calibration/calculate")
async def calculate_calibration(calibration_config: dict = None):
    """
    Calculate calibration transformation from collected points
    Backend computes transformation matrix and accuracy
    
    Supports both methods:
    - Homography transformation (preferred, fixes 500px+ errors)
    - Linear transformation (fallback for compatibility)
    """
    method = "homography"  # Default to homography for better accuracy
    use_opencv = True
    
    # Allow frontend to specify calibration method
    if calibration_config:
        method = calibration_config.get("method", "homography")
        use_opencv = calibration_config.get("use_opencv", True)
    
    logger.info(f"🔢 Calculating calibration transformation using {method} method")
    
    if method == "homography":
        result = gaze_manager.calculate_homography_calibration_transform(use_opencv=use_opencv)
    else:
        result = gaze_manager.calculate_calibration_transform()
    
    if result["success"]:
        method_used = result.get("method", "linear")
        return {
            "status": "success",
            "accuracy_px": result["accuracy_px"],
            "calibration_transform": result["transform"],
            "points_used": result["points_used"],
            "method": method_used,
            "message": f"{method_used.title()} calibration completed with {result['accuracy_px']:.1f}px accuracy",
            "timestamp": int(time.time() * 1000)
        }
    else:
        return {
            "status": "error",
            "message": result["message"],
            "timestamp": int(time.time() * 1000)
        }

@app.get("/api/calibration/status")
async def get_calibration_status():
    """Get current calibration status"""
    frontend_data = gaze_manager.get_frontend_data()
    return {
        "calibrated": frontend_data["calibration"]["calibrated"],
        "accuracy_px": frontend_data["calibration"]["accuracy_px"],
        "transform_loaded": gaze_manager.calibration_transform.get("calibrated", False),
        "calibration_method": gaze_manager.calibration_transform.get("method", "linear"),
        "calibration_in_progress": gaze_manager.is_calibrating if hasattr(gaze_manager, 'is_calibrating') else False,
        "timestamp": int(time.time() * 1000)
    }

@app.get("/api/calibration/camera_intrinsics")
async def get_camera_intrinsics():
    """
    Get scene camera intrinsic parameters for debugging and validation
    This endpoint helps verify proper camera parameter retrieval from Sol SDK
    """
    logger.info("📷 Retrieving scene camera intrinsic parameters")
    
    intrinsics = gaze_manager.get_scene_camera_intrinsics()
    
    if intrinsics:
        return {
            "status": "success",
            "camera_intrinsics": intrinsics,
            "source": intrinsics.get("source", "unknown"),
            "focal_length": intrinsics.get("focal_length", {}),
            "principal_point": intrinsics.get("principal_point", {}),
            "resolution": intrinsics.get("resolution", {}),
            "message": f"Camera intrinsics retrieved from {intrinsics.get('source', 'unknown')}",
            "timestamp": int(time.time() * 1000)
        }
    else:
        return {
            "status": "error",
            "message": "Failed to retrieve camera intrinsics",
            "sol_sdk_available": gaze_manager.sync_client is not None,
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
    print("   " Status: http://localhost:8000/api/status")
    print("   " Stream: http://localhost:8000/api/gaze/stream")
    print("   " Health: http://localhost:8000/api/health")
    print("   " Debug: http://localhost:8000/api/debug/info")
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