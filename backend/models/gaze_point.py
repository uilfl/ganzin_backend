#!/usr/bin/env python3
"""
GazePoint data model for Sol Glasses gaze tracking
Based on testing insights and Sol SDK data structure
"""

from dataclasses import dataclass, asdict
from typing import Optional
import time

@dataclass
class GazePoint:
    """
    Comprehensive gaze data structure supporting both 2D and 3D gaze tracking
    Based on Sol Glasses SDK and frontend integration testing
    """
    # Timestamp
    timestamp: float  # Unix timestamp in seconds (with millisecond precision)
    
    # 2D Gaze Data (screen coordinates)
    gaze_valid: int  # 0 or 1
    gaze_pos_x: float  # 2D screen pixel X coordinate
    gaze_pos_y: float  # 2D screen pixel Y coordinate
    
    # 3D Gaze Data (scene camera coordinate system)
    combined_3d_gaze_valid: int  # 0 or 1
    combined_3d_gaze_pos_x: float  # 3D position in mm (scene camera origin)
    combined_3d_gaze_pos_y: float  # 3D position in mm
    combined_3d_gaze_pos_z: float  # 3D position in mm
    combined_3d_gaze_dir_x: float  # 3D gaze direction vector
    combined_3d_gaze_dir_y: float  # 3D gaze direction vector
    combined_3d_gaze_dir_z: float  # 3D gaze direction vector
    
    # Pupil Data
    left_pupil_size: float  # Pupil diameter in mm
    right_pupil_size: float  # Pupil diameter in mm
    
    # Confidence and Quality
    confidence: float = 1.0  # Gaze confidence (0.0-1.0)
    
    # Calibrated Coordinates (transformed for frontend use)
    calibrated_x: Optional[float] = None  # Screen-calibrated X coordinate
    calibrated_y: Optional[float] = None  # Screen-calibrated Y coordinate
    
    @classmethod
    def from_sol_sdk(cls, sol_gaze_data, timestamp: Optional[float] = None) -> 'GazePoint':
        """
        Create GazePoint from Sol SDK gaze data structure
        
        Args:
            sol_gaze_data: Raw gaze data from Sol SDK
            timestamp: Optional timestamp override
        
        Returns:
            GazePoint instance
        """
        current_time = timestamp or time.time()
        
        # Extract 2D gaze data
        gaze_2d = sol_gaze_data.combined.gaze_2d
        gaze_3d = sol_gaze_data.combined.gaze_3d
        
        # Extract pupil data
        left_pupil = getattr(sol_gaze_data.left, 'pupil_size', 0.0)
        right_pupil = getattr(sol_gaze_data.right, 'pupil_size', 0.0)
        
        return cls(
            timestamp=current_time,
            gaze_valid=int(gaze_2d.valid),
            gaze_pos_x=float(gaze_2d.x),
            gaze_pos_y=float(gaze_2d.y),
            combined_3d_gaze_valid=int(gaze_3d.valid),
            combined_3d_gaze_pos_x=float(gaze_3d.position.x),
            combined_3d_gaze_pos_y=float(gaze_3d.position.y),
            combined_3d_gaze_pos_z=float(gaze_3d.position.z),
            combined_3d_gaze_dir_x=float(gaze_3d.direction.x),
            combined_3d_gaze_dir_y=float(gaze_3d.direction.y),
            combined_3d_gaze_dir_z=float(gaze_3d.direction.z),
            left_pupil_size=float(left_pupil),
            right_pupil_size=float(right_pupil),
            confidence=float(gaze_2d.valid)  # Use validity as confidence
        )
    
    @classmethod
    def create_mock(cls, x: float, y: float, confidence: float = 0.9) -> 'GazePoint':
        """
        Create mock gaze point for testing
        
        Args:
            x: Screen X coordinate
            y: Screen Y coordinate  
            confidence: Gaze confidence (0.0-1.0)
        
        Returns:
            Mock GazePoint instance
        """
        return cls(
            timestamp=time.time(),
            gaze_valid=1,
            gaze_pos_x=x,
            gaze_pos_y=y,
            combined_3d_gaze_valid=1,
            combined_3d_gaze_pos_x=x * 0.1,  # Mock 3D conversion
            combined_3d_gaze_pos_y=y * 0.1,
            combined_3d_gaze_pos_z=100.0,
            combined_3d_gaze_dir_x=0.0,
            combined_3d_gaze_dir_y=0.0,
            combined_3d_gaze_dir_z=-1.0,
            left_pupil_size=3.5,
            right_pupil_size=3.5,
            confidence=confidence
        )
    
    def apply_calibration_transform(self, transform: dict) -> None:
        """
        Apply calibration transformation to convert gaze coordinates
        Supports both homography (preferred) and linear transformation (fallback)
        
        Args:
            transform: Calibration transformation parameters
                For homography: homography_matrix (3x3), method="homography"
                For linear: scale_x, scale_y, offset_x, offset_y
        """
        if not transform.get("calibrated", False):
            self.calibrated_x = self.gaze_pos_x
            self.calibrated_y = self.gaze_pos_y
            return
        
        # Check transformation method
        if transform.get("method") == "homography" and "homography_matrix" in transform:
            # Apply homography transformation (accurate perspective correction)
            self._apply_homography_transform(transform)
        else:
            # Apply linear transformation (fallback for compatibility)
            self._apply_linear_transform(transform)
        
        # Clamp to screen bounds (configurable based on display resolution)
        max_x = transform.get("screen_width", 1920)
        max_y = transform.get("screen_height", 1080)
        
        self.calibrated_x = max(0, min(max_x, self.calibrated_x))
        self.calibrated_y = max(0, min(max_y, self.calibrated_y))
    
    def _apply_homography_transform(self, transform: dict) -> None:
        """
        Apply homography transformation for accurate perspective correction
        This fixes the 500px+ errors caused by linear scaling
        """
        try:
            import numpy as np
            
            # Get homography matrix from transform
            H = np.array(transform["homography_matrix"], dtype=np.float64)
            
            # Convert gaze point to homogeneous coordinates
            gaze_homogeneous = np.array([self.gaze_pos_x, self.gaze_pos_y, 1.0])
            
            # Apply homography transformation
            screen_homogeneous = H @ gaze_homogeneous
            
            # Convert back to 2D coordinates (perspective division)
            if abs(screen_homogeneous[2]) > 1e-8:  # Avoid division by zero
                self.calibrated_x = screen_homogeneous[0] / screen_homogeneous[2]
                self.calibrated_y = screen_homogeneous[1] / screen_homogeneous[2]
            else:
                # Fallback to linear transformation if homogeneous coordinate is invalid
                print("⚠️ Invalid homogeneous coordinate, falling back to linear transformation")
                self._apply_linear_transform(transform)
                
        except Exception as e:
            print(f"❌ Homography transformation failed: {e}, falling back to linear")
            self._apply_linear_transform(transform)
    
    def _apply_linear_transform(self, transform: dict) -> None:
        """
        Apply linear transformation (fallback method, less accurate)
        """
        # Apply linear calibration transformation (original method)
        self.calibrated_x = (self.gaze_pos_x * transform.get("scale_x", 1.0)) + transform.get("offset_x", 0.0)
        self.calibrated_y = (self.gaze_pos_y * transform.get("scale_y", 1.0)) + transform.get("offset_y", 0.0)
    
    def is_valid(self) -> bool:
        """Check if gaze data is valid and reliable"""
        return (self.gaze_valid == 1 and 
                self.confidence >= 0.5 and
                self.gaze_pos_x >= 0 and 
                self.gaze_pos_y >= 0)
    
    def to_frontend_format(self) -> dict:
        """
        Convert to frontend-compatible format for visualization
        
        Returns:
            Dictionary suitable for frontend consumption
        """
        return {
            "x": self.calibrated_x or self.gaze_pos_x,
            "y": self.calibrated_y or self.gaze_pos_y,
            "timestamp": int(self.timestamp * 1000),  # Convert to milliseconds
            "confidence": self.confidence,
            "valid": self.is_valid()
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)