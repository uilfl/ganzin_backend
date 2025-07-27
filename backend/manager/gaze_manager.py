#!/usr/bin/env python3
"""
GazeDataManager - DIRECTLY using official Sol SDK examples
Following project_structure.md guidance: "直接抄進 GazeDataManager"
"""

import sys
import os
import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import asdict

# Add paths for Sol SDK (exactly like official examples)
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '../..')))
sys.path.append(os.path.abspath(os.path.join(current_dir, '../../examples')))

try:
    # DIRECT imports from official examples
    from utils.server_info import get_ip_and_port
    from ganzin.sol_sdk.synchronous.models import StreamingMode
    from ganzin.sol_sdk.synchronous.sync_client import SyncClient
    from ganzin.sol_sdk.responses import CaptureResult
    from ganzin.sol_sdk.requests import AddTagRequest, TagColor
    SOL_SDK_AVAILABLE = True
except ImportError:
    print("Warning: Sol SDK not available, using mock mode")
    SOL_SDK_AVAILABLE = False

# Import our data models
from models.gaze_point import GazePoint
from models.aoi_element import AOIElement, AOICollection  
from models.hit_log import HitLog, HitLogManager
from models.achievement import Achievement, AchievementManager

class GazeDataManager:
    """
    Following project_structure.md guidance EXACTLY:
    "把 sample 中的串流初始化、事件 loop、資料欄位 mapping 直接抄進 GazeDataManager"
    """
    
    def __init__(self):
        # Sol SDK components (EXACTLY like gaze_streaming.py)
        self.sync_client: Optional[SyncClient] = None
        self.streaming_thread = None
        self.is_streaming = False
        
        # Data storage (following project structure)
        self.gaze_trail: List[GazePoint] = []
        self.aoi_collection = AOICollection()
        self.hit_log_manager: Optional[HitLogManager] = None
        self.achievement_manager: Optional[AchievementManager] = None
        
        # Session management
        self.current_session_id: Optional[str] = None
        self.session_start_time: Optional[float] = None
        self.total_samples = 0
        
        # Calibration (from our testing)
        self.calibration_transform = self._load_calibration()
        
        # Real-time data for frontend
        self.current_gaze: Optional[GazePoint] = None
        self.recent_hits: List[HitLog] = []
        self.current_cognitive_load: Optional[Dict] = None
        self.cognitive_load_history: List[Dict] = []
        self.vocabulary_discoveries: List[str] = []
        
        # Calibration state management (following your decision: 後端負責計算轉換與保存參數)
        self.is_calibrating = False
        self.calibration_points = []  # Store calibration samples
        
        # Initialize AOIs
        self.aoi_collection.create_standard_lesson_aois()
    
    def _load_calibration(self) -> Dict:
        """Load calibration from testing phase"""
        try:
            calibration_file = os.path.join(os.path.dirname(__file__), '../../backend_test/sol_glasses_calibration.json')
            with open(calibration_file, 'r') as f:
                calibration_data = json.load(f)
            print(f"✅ Loaded calibration: {calibration_data['transform']['accuracy_px']:.1f}px accuracy")
            return calibration_data['transform']
        except FileNotFoundError:
            print("⚠️ No calibration file found")
            return {"scale_x": 1.0, "scale_y": 1.0, "offset_x": 0.0, "offset_y": 0.0, "calibrated": False}
        except Exception as e:
            print(f"❌ Failed to load calibration: {e}")
            return {"scale_x": 1.0, "scale_y": 1.0, "offset_x": 0.0, "offset_y": 0.0, "calibrated": False}
    
    def start_streaming_session(self, session_id: str) -> bool:
        """
        Start streaming session using EXACT official gaze_streaming.py pattern
        Following project_structure.md: "官方 sample gaze_streaming.py 展示了如何連線、啟動 gaze 資料串流"
        """
        if self.is_streaming:
            print("⚠️ Already streaming")
            return True
        
        self.current_session_id = session_id
        self.session_start_time = time.time()
        self.hit_log_manager = HitLogManager(session_id)
        self.achievement_manager = AchievementManager(session_id)  # 新增：成就系統
        self.total_samples = 0
        
        if not SOL_SDK_AVAILABLE:
            return self._start_mock_streaming()
        
        try:
            # EXACT pattern from gaze_streaming.py main()
            address, port = get_ip_and_port()
            self.sync_client = SyncClient(address, port)
            
            # EXACT pattern: create_streaming_thread
            self.streaming_thread = self.sync_client.create_streaming_thread(StreamingMode.GAZE)
            self.streaming_thread.start()
            
            self.is_streaming = True
            
            # Start the processing loop (extracted from gaze_streaming.py)
            self._start_gaze_processing_loop()
            
            print(f"✅ Started Sol Glasses streaming: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start streaming: {e}")
            return self._start_mock_streaming()
    
    def _start_gaze_processing_loop(self):
        """
        EXACT extraction from gaze_streaming.py main() function
        Following project_structure.md: "直接抄進 GazeDataManager 裡的 streaming thread"
        """
        def gaze_processing_worker():
            try:
                while self.is_streaming:
                    # EXACT pattern from gaze_streaming.py line 20-22
                    gazes = self.sync_client.get_gazes_from_streaming(timeout=5.0)
                    for gaze in gazes:
                        # EXACT pattern: print(f'gaze: x = {gaze.combined.gaze_2d.x}, y = {gaze.combined.gaze_2d.y}')
                        # But we process instead of just printing
                        self._process_gaze_sample_from_sdk(gaze)
                        
            except KeyboardInterrupt:
                # EXACT pattern from gaze_streaming.py line 23
                pass
            except Exception as ex:
                # EXACT pattern from gaze_streaming.py line 25-26
                if self.is_streaming:
                    print(ex)
            finally:
                # EXACT pattern from gaze_streaming.py line 27
                print('Gaze processing stopped')
        
        # Start in background thread
        processing_thread = threading.Thread(target=gaze_processing_worker, daemon=True)
        processing_thread.start()
    
    def _process_gaze_sample_from_sdk(self, gaze):
        """
        Process gaze sample using EXACT SDK data structure
        Based on gaze_streaming.py: gaze.combined.gaze_2d.x, gaze.combined.gaze_2d.y
        """
        # Create GazePoint from exact SDK structure
        gaze_point = GazePoint.from_sol_sdk(gaze)
        
        # Apply calibration
        gaze_point.apply_calibration_transform(self.calibration_transform)
        
        # Update current gaze
        self.current_gaze = gaze_point
        
        # Add to trail
        self.gaze_trail.append(gaze_point)
        if len(self.gaze_trail) > 20:
            self.gaze_trail.pop(0)
        
        # Update stats
        self.total_samples += 1
        
        # Update cognitive load (every 5 seconds or 100 samples)
        if self.total_samples % 100 == 0 or len(self.gaze_trail) >= 10:
            self._update_cognitive_load()
        
        # AOI processing
        if gaze_point.is_valid():
            self._process_aoi_hits(gaze_point)
    
    def capture_snapshot_with_gaze(self) -> Optional[dict]:
        """
        DIRECT implementation from capture_frame_and_gaze.py
        Following project_structure.md: "做成你 GazeDataManager 內的 capture_snapshot_with_gaze() 函數"
        """
        if not self.sync_client or not SOL_SDK_AVAILABLE:
            return None
        
        try:
            # EXACT pattern from capture_frame_and_gaze.py lines 14-15
            resp = self.sync_client.capture()
            result = CaptureResult.from_raw(resp.result)
            
            # EXACT pattern from capture_frame_and_gaze.py line 17
            gaze_x = result.gaze_data.combined.gaze_2d.x
            gaze_y = result.gaze_data.combined.gaze_2d.y
            
            # Save image (EXACT pattern from lines 18-20)
            timestamp = int(time.time())
            image_filename = f"data/snapshot_{self.current_session_id}_{timestamp}.jpg"
            os.makedirs(os.path.dirname(image_filename), exist_ok=True)
            
            with open(image_filename, "wb") as file:
                file.write(result.scene_image)
                print(f'Saved snapshot to "{file.name}"')
            
            return {
                "timestamp": result.timestamp,
                "gaze_x": gaze_x,
                "gaze_y": gaze_y,
                "image_filename": image_filename
            }
            
        except Exception as e:
            print(f"❌ Snapshot capture failed: {e}")
            return None
    
    def get_scene_camera_intrinsics(self) -> Optional[dict]:
        """
        Get scene camera intrinsic parameters using proper Sol SDK pattern
        Following your guidance: sc.get_scene_camera_param() -> resp.result.camera_param
        
        Returns camera intrinsic parameters needed for homography transformation:
        - intrinsic: 3x3 camera matrix [fx, 0, cx; 0, fy, cy; 0, 0, 1]
        - distortion: distortion coefficients for lens correction
        - resolution: scene camera resolution for coordinate mapping
        """
        if not self.sync_client or not SOL_SDK_AVAILABLE:
            print("⚠️ Sol SDK not available, returning mock camera parameters")
            # Return mock parameters for testing homography transformation
            return {
                "intrinsic": [[800.0, 0.0, 400.0], [0.0, 800.0, 300.0], [0.0, 0.0, 1.0]],
                "distortion": [0.0, 0.0, 0.0, 0.0, 0.0],
                "resolution": {"width": 800, "height": 600},
                "focal_length": {"fx": 800.0, "fy": 800.0},
                "principal_point": {"cx": 400.0, "cy": 300.0},
                "source": "mock_data"
            }
        
        try:
            # Step 2: 取得 camera param (following your pattern)
            resp = self.sync_client.get_scene_camera_param()
            
            # Step 3: 檢查 status & 取出參數 (following your pattern)
            if resp.status.code == 0:  # 0 usually means success
                cam_param = resp.result.camera_param
                
                print("📷 Scene camera intrinsic:", cam_param.intrinsic)
                print("📷 Scene camera distortion:", cam_param.distort)
                
                # Convert to standardized format for homography calculation
                intrinsic_matrix = cam_param.intrinsic  # Should be 3x3 matrix
                distortion_coeffs = cam_param.distort   # Distortion coefficients
                
                # Extract focal lengths and principal point from intrinsic matrix
                # Standard camera matrix format: [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]
                fx = intrinsic_matrix[0][0] if len(intrinsic_matrix) >= 3 else 800.0
                fy = intrinsic_matrix[1][1] if len(intrinsic_matrix) >= 3 else 800.0
                cx = intrinsic_matrix[0][2] if len(intrinsic_matrix) >= 3 else 400.0
                cy = intrinsic_matrix[1][2] if len(intrinsic_matrix) >= 3 else 300.0
                
                # Get resolution (might be in different field)
                resolution = getattr(cam_param, 'resolution', None)
                if not resolution:
                    # Try to get from other fields or use defaults
                    resolution = {"width": 800, "height": 600}
                
                camera_intrinsics = {
                    "intrinsic": intrinsic_matrix,
                    "distortion": distortion_coeffs,
                    "resolution": resolution,
                    "focal_length": {"fx": fx, "fy": fy},
                    "principal_point": {"cx": cx, "cy": cy},
                    "source": "sol_sdk"
                }
                
                print(f"✅ Camera intrinsics extracted: fx={fx:.1f}, fy={fy:.1f}, cx={cx:.1f}, cy={cy:.1f}")
                return camera_intrinsics
                
            else:
                print(f"❌ Get scene camera param failed: {resp.status.message}")
                return None
            
        except Exception as e:
            print(f"❌ Failed to get camera parameters: {e}")
            return None
    
    def add_aoi_hit_tag(self, aoi_id: str, description: str = "") -> bool:
        """
        DIRECT implementation from add_tag.py
        Following project_structure.md: "改為「AOI hit」時自動寫 hit_log.json"
        """
        if not self.sync_client or not SOL_SDK_AVAILABLE:
            return False
        
        try:
            # EXACT pattern from add_tag.py lines 14-16
            color = TagColor.LightSeaGreen
            timestamp = int(time.time() * 1000)  # Milliseconds
            tag_name = f"AOI_HIT_{aoi_id}"
            
            req = AddTagRequest(tag_name, description, timestamp, color)
            resp = self.sync_client.add_tag(req)
            
            print(f'🏷️ Added AOI hit tag: {aoi_id} -> {resp}')
            return True
            
        except Exception as e:
            print(f"❌ Failed to add tag: {e}")
            return False
    
    def _process_aoi_hits(self, gaze_point: GazePoint):
        """Process AOI hits with tag logging"""
        hit_x = gaze_point.calibrated_x or gaze_point.gaze_pos_x
        hit_y = gaze_point.calibrated_y or gaze_point.gaze_pos_y
        
        hit_aoi = self.aoi_collection.find_hit(hit_x, hit_y)
        
        if hit_aoi and self.hit_log_manager:
            # Create hit log
            hit_log = HitLog.create_from_gaze_and_aoi(
                gaze_point, hit_aoi, "2d", self.current_session_id
            )
            
            self.recent_hits.append(hit_log)
            if len(self.recent_hits) > 10:
                self.recent_hits.pop(0)
            
            # For vocabulary words, add tag (following project_structure.md guidance)
            if hit_aoi.vocabulary_word:
                hit_log.fixation_duration = 1.5
                self.hit_log_manager.add_hit(hit_log)
                
                # Add tag using official add_tag.py pattern
                self.add_aoi_hit_tag(hit_aoi.id, f"Vocabulary hit: {hit_aoi.text}")
                
                print(f"🎯 Vocabulary hit: {hit_aoi.text} at ({hit_x:.1f}, {hit_y:.1f})")
                
                # Add to vocabulary discoveries for SSE
                if hit_aoi.text not in self.vocabulary_discoveries:
                    self.vocabulary_discoveries.append(hit_aoi.text)
                    # Keep only last 10 discoveries
                    if len(self.vocabulary_discoveries) > 10:
                        self.vocabulary_discoveries.pop(0)
                    
                    # Update achievement progress (following your decision: 後端統一維護)
                    if self.achievement_manager:
                        newly_unlocked = self.achievement_manager.update_vocabulary_progress(
                            len(self.vocabulary_discoveries)
                        )
                        # Log achievement unlocks for frontend notification
                        for achievement in newly_unlocked:
                            print(f"🏆 New achievement unlocked: {achievement.title}")
    
    def _update_cognitive_load(self):
        """
        Calculate real-time cognitive load for SSE stream
        Based on gaze dispersion and movement patterns
        """
        if len(self.gaze_trail) < 5:
            return
        
        # Get recent gaze points for analysis
        recent_points = self.gaze_trail[-10:] if len(self.gaze_trail) >= 10 else self.gaze_trail
        
        # Calculate gaze dispersion
        x_coords = [p.gaze_pos_x for p in recent_points]
        y_coords = [p.gaze_pos_y for p in recent_points]
        
        x_range = max(x_coords) - min(x_coords) if len(x_coords) > 1 else 0
        y_range = max(y_coords) - min(y_coords) if len(y_coords) > 1 else 0
        dispersion = (x_range + y_range) / 2
        
        # Calculate movement velocity
        velocities = []
        for i in range(1, len(recent_points)):
            dx = recent_points[i].gaze_pos_x - recent_points[i-1].gaze_pos_x
            dy = recent_points[i].gaze_pos_y - recent_points[i-1].gaze_pos_y
            dt = recent_points[i].timestamp - recent_points[i-1].timestamp
            if dt > 0:
                velocity = (dx*dx + dy*dy)**0.5 / dt
                velocities.append(velocity)
        
        avg_velocity = sum(velocities) / len(velocities) if velocities else 0
        
        # Convert to cognitive load score (0-100)
        dispersion_score = min(100, dispersion / 5)  # Normalize dispersion
        velocity_score = min(100, avg_velocity / 100)  # Normalize velocity
        
        # Combine scores (higher dispersion + higher velocity = higher cognitive load)
        cognitive_score = (dispersion_score * 0.6 + velocity_score * 0.4)
        
        # Determine level and color
        if cognitive_score < 30:
            level, color = "LOW", "green"
        elif cognitive_score < 70:
            level, color = "MEDIUM", "orange"
        else:
            level, color = "HIGH", "red"
        
        # Update current cognitive load
        self.current_cognitive_load = {
            "score": round(cognitive_score, 1),
            "level": level,
            "color": color,
            "timestamp": time.time(),
            "metrics": {
                "gaze_dispersion": round(dispersion, 2),
                "avg_velocity": round(avg_velocity, 2),
                "sample_count": len(recent_points)
            }
        }
        
        # Add to history (keep last 20 entries for trend analysis)
        self.cognitive_load_history.append(self.current_cognitive_load.copy())
        if len(self.cognitive_load_history) > 20:
            self.cognitive_load_history.pop(0)
        
        # Update focus achievements based on session duration
        if self.achievement_manager and self.session_start_time:
            session_duration = time.time() - self.session_start_time
            newly_unlocked = self.achievement_manager.update_focus_progress(session_duration)
            for achievement in newly_unlocked:
                print(f"🏆 Focus achievement unlocked: {achievement.title}")
    
    def _start_mock_streaming(self) -> bool:
        """Mock streaming for testing"""
        import random
        
        def mock_worker():
            while self.is_streaming:
                try:
                    # Create mock gaze that matches SDK structure
                    mock_gaze = type('MockGaze', (), {
                        'combined': type('Combined', (), {
                            'gaze_2d': type('Gaze2D', (), {
                                'x': 400 + random.uniform(-200, 200),
                                'y': 400 + random.uniform(-200, 200),
                                'valid': 1
                            })(),
                            'gaze_3d': type('Gaze3D', (), {
                                'position': type('Position', (), {
                                    'x': random.uniform(-50, 50),
                                    'y': random.uniform(-50, 50),
                                    'z': 100.0
                                })(),
                                'direction': type('Direction', (), {
                                    'x': 0.0, 'y': 0.0, 'z': -1.0
                                })(),
                                'valid': 1
                            })()
                        })(),
                        'left': type('Left', (), {'pupil_size': 3.5})(),
                        'right': type('Right', (), {'pupil_size': 3.5})()
                    })()
                    
                    self._process_gaze_sample_from_sdk(mock_gaze)
                    time.sleep(1.0 / 60.0)
                    
                except Exception as e:
                    print(f"Mock streaming error: {e}")
                    time.sleep(0.1)
        
        self.is_streaming = True
        mock_thread = threading.Thread(target=mock_worker, daemon=True)
        mock_thread.start()
        
        print(f"✅ Started mock streaming: {self.current_session_id}")
        return True
    
    def stop_streaming_session(self) -> Optional[str]:
        """
        Stop streaming using EXACT official pattern
        Following gaze_streaming.py cleanup in finally block
        """
        if not self.is_streaming:
            return None
        
        self.is_streaming = False
        
        # EXACT pattern from gaze_streaming.py lines 30-31
        if self.streaming_thread:
            try:
                self.streaming_thread.cancel()
                self.streaming_thread.join()
            except Exception as e:
                print(f"Thread cleanup error: {e}")
        
        # Export session data
        if self.hit_log_manager and self.current_session_id:
            session_data = self._export_session_data()
            filename = f"data/session_{self.current_session_id}_{int(time.time())}.json"
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            try:
                with open(filename, 'w') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
                print(f"💾 Session exported: {filename}")
                return filename
            except Exception as e:
                print(f"❌ Export failed: {e}")
        
        return None
    
    def _export_session_data(self) -> dict:
        """Export session data following project_structure.md export pattern"""
        duration = time.time() - (self.session_start_time or time.time())
        
        return {
            "session_id": self.current_session_id,
            "start_time": self.session_start_time,
            "end_time": time.time(),
            "duration_seconds": duration,
            "gaze_trail": [gaze.to_dict() for gaze in self.gaze_trail],
            "total_samples": self.total_samples,
            "samples_per_second": self.total_samples / max(duration, 1),
            "aois": self.aoi_collection.to_frontend_format(),
            "hit_log": self.hit_log_manager.export_session_data() if self.hit_log_manager else {},
            "calibration": {
                "calibrated": self.calibration_transform.get("calibrated", False),
                "accuracy_px": self.calibration_transform.get("accuracy_px", 0)
            }
        }
    
    def get_frontend_data(self) -> dict:
        """
        Enhanced frontend data including cognitive load and vocabulary discoveries
        Following your decision: 後端即時計算，直接丟到 SSE stream 讓前端展示
        """
        return {
            "gaze": {
                "current": self.current_gaze.to_frontend_format() if self.current_gaze else None,
                "trail": [gaze.to_frontend_format() for gaze in self.gaze_trail[-5:]],
                "is_streaming": self.is_streaming
            },
            "aoi_hits": {
                "recent": [hit.to_frontend_format() for hit in self.recent_hits[-3:]],
                "total_hits": len(self.recent_hits),
                "vocabulary_discoveries": self.vocabulary_discoveries.copy()  # 新增：單字發現列表
            },
            # 新增：即時認知負荷資料
            "cognitive_load": {
                "current": self.current_cognitive_load,
                "history": self.cognitive_load_history[-10:] if self.cognitive_load_history else []  # Last 10 for trend
            },
            # 新增：成就系統資料（following your decision: 後端統一維護與存檔）
            "achievements": self.achievement_manager.to_frontend_format() if self.achievement_manager else {
                "recent_unlocks": [],
                "total_unlocked": 0,
                "total_points": 0
            },
            "session": {
                "session_id": self.current_session_id,
                "total_samples": self.total_samples,
                "duration": time.time() - (self.session_start_time or time.time()) if self.session_start_time else 0,
                "connected": self.is_streaming,
                "vocabulary_count": len(self.vocabulary_discoveries)  # 新增：單字數量
            },
            "aois": self.aoi_collection.to_frontend_format(),
            "calibration": {
                "calibrated": self.calibration_transform.get("calibrated", False),
                "accuracy_px": self.calibration_transform.get("accuracy_px", 0)
            }
        }
    
    def add_dynamic_aoi(self, aoi_data: dict) -> bool:
        """Add dynamic AOI from frontend"""
        try:
            aoi = AOIElement.from_frontend_aoi(aoi_data)
            self.aoi_collection.add_element(aoi)
            print(f"➕ Added dynamic AOI: {aoi.id}")
            return True
        except Exception as e:
            print(f"❌ Failed to add AOI: {e}")
            return False
    
    def get_session_statistics(self) -> dict:
        """Get session statistics"""
        if not self.hit_log_manager:
            return {}
        
        return {
            "vocabulary_discoveries": len(self.hit_log_manager.get_vocabulary_hits()),
            "total_fixations": len(self.hit_log_manager.get_long_fixations()),
            "aoi_statistics": self.hit_log_manager.get_aoi_statistics(),
            "session_duration": time.time() - (self.session_start_time or time.time()) if self.session_start_time else 0,
            "samples_collected": self.total_samples
        }
    
    def start_calibration_process(self) -> bool:
        """
        Start calibration process
        Following your decision: 前端 UI 流程控制、後端負責計算轉換與保存參數
        """
        self.is_calibrating = True
        self.calibration_points = []
        print("🎯 Calibration process started - ready to collect points")
        return True
    
    def capture_calibration_point(self, point_index: int, screen_x: float, screen_y: float) -> tuple[bool, Optional[dict]]:
        """
        Capture calibration point with current gaze data
        Backend responsibility: Capture and store gaze coordinates
        """
        if not self.is_calibrating:
            return False, None
        
        if not self.current_gaze:
            return False, None
        
        # Create calibration sample
        calibration_sample = {
            "point_index": point_index,
            "screen_x": screen_x,
            "screen_y": screen_y,
            "gaze_x": self.current_gaze.gaze_pos_x,
            "gaze_y": self.current_gaze.gaze_pos_y,
            "confidence": self.current_gaze.confidence,
            "timestamp": time.time()
        }
        
        self.calibration_points.append(calibration_sample)
        
        print(f"📍 Captured point {point_index}: screen({screen_x}, {screen_y}) -> gaze({self.current_gaze.gaze_pos_x:.1f}, {self.current_gaze.gaze_pos_y:.1f})")
        
        return True, calibration_sample
    
    def calculate_homography_calibration_transform(self, use_opencv: bool = True) -> dict:
        """
        Calculate calibration transformation using homography matrix instead of linear scaling
        This replaces the flawed linear transformation that causes 500px+ errors
        
        Args:
            use_opencv: Whether to use OpenCV for robust homography calculation
        
        Returns:
            Calibration result with homography matrix and accuracy metrics
        """
        if len(self.calibration_points) < 4:
            return {
                "success": False,
                "message": f"Need at least 4 points for homography, got {len(self.calibration_points)}"
            }
        
        try:
            # Get camera intrinsics for proper perspective transformation
            camera_intrinsics = self.get_scene_camera_intrinsics()
            if not camera_intrinsics:
                print("⚠️ No camera intrinsics available, falling back to linear transformation")
                return self._calculate_linear_calibration_fallback()
            
            # Extract calibration point pairs
            scene_points = []  # Gaze coordinates in scene camera space
            screen_points = []  # Target coordinates in screen space
            
            for point in self.calibration_points:
                scene_points.append([point["gaze_x"], point["gaze_y"]])
                screen_points.append([point["screen_x"], point["screen_y"]])
            
            print(f"🔢 Computing homography with {len(scene_points)} point pairs")
            print(f"📷 Using camera intrinsics: fx={camera_intrinsics['focal_length']['fx']:.1f}")
            
            if use_opencv:
                # Use OpenCV for robust homography calculation (preferred)
                homography_matrix, accuracy = self._calculate_opencv_homography(scene_points, screen_points)
            else:
                # Use manual homography calculation (fallback)
                homography_matrix, accuracy = self._calculate_manual_homography(scene_points, screen_points)
            
            if homography_matrix is None:
                print("❌ Homography calculation failed, falling back to linear")
                return self._calculate_linear_calibration_fallback()
            
            # Create transformation dictionary with homography
            transform = {
                "method": "homography",
                "homography_matrix": homography_matrix.tolist() if hasattr(homography_matrix, 'tolist') else homography_matrix,
                "camera_intrinsics": camera_intrinsics,
                "accuracy_px": accuracy,
                "calibrated": True,
                "points_used": len(self.calibration_points),
                "timestamp": time.time(),
                # Keep legacy fields for compatibility
                "scale_x": 1.0,
                "scale_y": 1.0, 
                "offset_x": 0.0,
                "offset_y": 0.0
            }
            
            # Save and apply calibration
            self.calibration_transform = transform
            self._save_calibration(transform)
            self.is_calibrating = False
            
            print(f"✅ Homography calibration completed: {accuracy:.1f}px accuracy")
            
            return {
                "success": True,
                "accuracy_px": accuracy,
                "transform": transform,
                "points_used": len(self.calibration_points),
                "method": "homography"
            }
            
        except Exception as e:
            print(f"❌ Homography calibration failed: {e}")
            print("⚠️ Falling back to linear calibration")
            return self._calculate_linear_calibration_fallback()
    
    def _calculate_opencv_homography(self, scene_points, screen_points):
        """Calculate homography using OpenCV (robust method)"""
        try:
            import cv2
            import numpy as np
            
            # Convert to numpy arrays
            src_pts = np.array(scene_points, dtype=np.float32)
            dst_pts = np.array(screen_points, dtype=np.float32)
            
            # Calculate homography with RANSAC for robustness
            homography_matrix, mask = cv2.findHomography(
                src_pts, dst_pts, 
                cv2.RANSAC, 
                ransacReprojThreshold=5.0
            )
            
            # Calculate accuracy using the homography
            accuracy_errors = []
            for i, (scene_pt, screen_pt) in enumerate(zip(scene_points, screen_points)):
                # Transform scene point to screen coordinates
                scene_homogeneous = np.array([scene_pt[0], scene_pt[1], 1.0])
                screen_predicted = homography_matrix @ scene_homogeneous
                screen_predicted = screen_predicted[:2] / screen_predicted[2]  # Normalize
                
                # Calculate error
                error = np.sqrt((screen_predicted[0] - screen_pt[0])**2 + (screen_predicted[1] - screen_pt[1])**2)
                accuracy_errors.append(error)
            
            avg_accuracy = np.mean(accuracy_errors)
            print(f"📐 OpenCV homography accuracy: {avg_accuracy:.2f}px (errors: {[f'{e:.1f}' for e in accuracy_errors]})")
            
            return homography_matrix, avg_accuracy
            
        except ImportError:
            print("⚠️ OpenCV not available, using manual homography calculation")
            return self._calculate_manual_homography(scene_points, screen_points)
        except Exception as e:
            print(f"❌ OpenCV homography calculation failed: {e}")
            return None, None
    
    def _calculate_manual_homography(self, scene_points, screen_points):
        """Manual homography calculation (fallback when OpenCV not available)"""
        try:
            import numpy as np
            
            # Minimum 4 points needed for homography
            if len(scene_points) < 4:
                return None, None
            
            # Build the equation system Ah = 0 for homography calculation
            A = []
            for (x, y), (u, v) in zip(scene_points, screen_points):
                A.append([-x, -y, -1, 0, 0, 0, x*u, y*u, u])
                A.append([0, 0, 0, -x, -y, -1, x*v, y*v, v])
            
            A = np.array(A)
            
            # Solve using SVD
            _, _, V = np.linalg.svd(A)
            h = V[-1, :]
            
            # Reshape to 3x3 homography matrix
            homography_matrix = h.reshape((3, 3))
            
            # Calculate accuracy
            accuracy_errors = []
            for scene_pt, screen_pt in zip(scene_points, screen_points):
                scene_homogeneous = np.array([scene_pt[0], scene_pt[1], 1.0])
                screen_predicted = homography_matrix @ scene_homogeneous
                screen_predicted = screen_predicted[:2] / screen_predicted[2]
                
                error = np.sqrt((screen_predicted[0] - screen_pt[0])**2 + (screen_predicted[1] - screen_pt[1])**2)
                accuracy_errors.append(error)
            
            avg_accuracy = np.mean(accuracy_errors)
            print(f"📐 Manual homography accuracy: {avg_accuracy:.2f}px")
            
            return homography_matrix, avg_accuracy
            
        except Exception as e:
            print(f"❌ Manual homography calculation failed: {e}")
            return None, None
    
    def _calculate_linear_calibration_fallback(self) -> dict:
        """Fallback to linear calibration when homography fails"""
        print("⚠️ Using linear calibration fallback (less accurate)")
        return self.calculate_calibration_transform()

    def calculate_calibration_transform(self) -> dict:
        """
        Calculate calibration transformation matrix
        Backend responsibility: Compute transformation and save parameters
        """
        if len(self.calibration_points) < 4:
            return {
                "success": False,
                "message": f"Need at least 4 points, got {len(self.calibration_points)}"
            }
        
        try:
            # Extract screen and gaze coordinates
            screen_points = [(p["screen_x"], p["screen_y"]) for p in self.calibration_points]
            gaze_points = [(p["gaze_x"], p["gaze_y"]) for p in self.calibration_points]
            
            # Calculate transformation using least squares
            # Simple linear transformation: screen = scale * gaze + offset
            gaze_x_vals = [p[0] for p in gaze_points]
            gaze_y_vals = [p[1] for p in gaze_points]
            screen_x_vals = [p[0] for p in screen_points]
            screen_y_vals = [p[1] for p in screen_points]
            
            # Calculate scale and offset for X
            if len(set(gaze_x_vals)) > 1:  # Avoid division by zero
                scale_x = (max(screen_x_vals) - min(screen_x_vals)) / (max(gaze_x_vals) - min(gaze_x_vals))
                offset_x = sum(screen_x_vals) / len(screen_x_vals) - scale_x * sum(gaze_x_vals) / len(gaze_x_vals)
            else:
                scale_x, offset_x = 1.0, 0.0
            
            # Calculate scale and offset for Y
            if len(set(gaze_y_vals)) > 1:  # Avoid division by zero
                scale_y = (max(screen_y_vals) - min(screen_y_vals)) / (max(gaze_y_vals) - min(gaze_y_vals))
                offset_y = sum(screen_y_vals) / len(screen_y_vals) - scale_y * sum(gaze_y_vals) / len(gaze_y_vals)
            else:
                scale_y, offset_y = 1.0, 0.0
            
            # Calculate accuracy by testing transformation on calibration points
            errors = []
            for point in self.calibration_points:
                predicted_x = point["gaze_x"] * scale_x + offset_x
                predicted_y = point["gaze_y"] * scale_y + offset_y
                error = ((predicted_x - point["screen_x"])**2 + (predicted_y - point["screen_y"])**2)**0.5
                errors.append(error)
            
            accuracy_px = sum(errors) / len(errors)
            
            # Create transformation dictionary
            transform = {
                "scale_x": scale_x,
                "scale_y": scale_y,
                "offset_x": offset_x,
                "offset_y": offset_y,
                "accuracy_px": accuracy_px,
                "calibrated": True,
                "points_used": len(self.calibration_points),
                "timestamp": time.time()
            }
            
            # Save calibration
            self.calibration_transform = transform
            self._save_calibration(transform)
            
            # End calibration process
            self.is_calibrating = False
            
            print(f"✅ Calibration completed: {accuracy_px:.1f}px accuracy using {len(self.calibration_points)} points")
            
            return {
                "success": True,
                "accuracy_px": accuracy_px,
                "transform": transform,
                "points_used": len(self.calibration_points)
            }
            
        except Exception as e:
            print(f"❌ Calibration calculation failed: {e}")
            self.is_calibrating = False
            return {
                "success": False,
                "message": f"Calibration calculation failed: {str(e)}"
            }
    
    def _save_calibration(self, transform: dict):
        """Save calibration to file"""
        try:
            calibration_data = {
                "transform": transform,
                "calibration_points": self.calibration_points,
                "created_at": time.time()
            }
            
            calibration_file = os.path.join(os.path.dirname(__file__), '../../backend_test/sol_glasses_calibration.json')
            os.makedirs(os.path.dirname(calibration_file), exist_ok=True)
            
            with open(calibration_file, 'w') as f:
                json.dump(calibration_data, f, indent=2)
            
            print(f"💾 Calibration saved to {calibration_file}")
            
        except Exception as e:
            print(f"❌ Failed to save calibration: {e}")