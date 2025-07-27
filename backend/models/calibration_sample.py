#!/usr/bin/env python3
"""
Calibration Sample data model
For storing calibration points during the calibration process
"""

from dataclasses import dataclass
import time

@dataclass
class CalibrationSample:
    """
    Single calibration sample point
    Based on data_schema.json specification
    """
    gaze_x: float  # Gaze coordinate (0-1 normalized)
    gaze_y: float  # Gaze coordinate (0-1 normalized)
    screen_x: float  # Target screen coordinate (pixels)
    screen_y: float  # Target screen coordinate (pixels)
    timestamp: float = None  # When sample was captured
    confidence: float = 1.0  # Gaze confidence for this sample
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "gaze_x": self.gaze_x,
            "gaze_y": self.gaze_y, 
            "screen_x": self.screen_x,
            "screen_y": self.screen_y,
            "timestamp": self.timestamp,
            "confidence": self.confidence
        }