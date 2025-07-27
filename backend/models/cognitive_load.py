#!/usr/bin/env python3
"""
Cognitive Load data model
For tracking cognitive load metrics during sessions
"""

from dataclasses import dataclass
import time

@dataclass
class CognitiveLoad:
    """
    Cognitive load measurement
    Based on gaze dispersion and other metrics
    """
    score: float  # Cognitive load score (0-100)
    level: str  # "LOW", "MEDIUM", "HIGH"
    color: str  # Color for UI display
    timestamp: float = None  # When measurement was taken
    
    # Detailed metrics (optional)
    fixation_rate: float = 0.0  # Fixations per second
    avg_fixation_duration: float = 0.0  # Average fixation duration
    saccade_velocity: float = 0.0  # Average saccade velocity
    pupil_dilation: float = 0.0  # Pupil dilation metric
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    @classmethod
    def calculate_from_gaze_trail(cls, gaze_trail, window_seconds: float = 5.0) -> 'CognitiveLoad':
        """
        Calculate cognitive load from recent gaze data
        
        Args:
            gaze_trail: List of recent gaze points
            window_seconds: Time window for calculation
        
        Returns:
            CognitiveLoad instance
        """
        if len(gaze_trail) < 3:
            return cls(score=0.0, level="LOW", color="green")
        
        # Simple cognitive load based on gaze dispersion
        recent_points = gaze_trail[-10:]  # Last 10 points
        x_coords = [p.gaze_pos_x for p in recent_points]
        y_coords = [p.gaze_pos_y for p in recent_points]
        
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        dispersion = (x_range + y_range) / 2
        
        # Convert to 0-100 scale
        score = min(100, max(0, dispersion / 3))
        
        # Determine level and color
        if score < 30:
            level, color = "LOW", "green"
        elif score < 70:
            level, color = "MEDIUM", "orange"
        else:
            level, color = "HIGH", "red"
        
        return cls(score=score, level=level, color=color)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "score": self.score,
            "level": self.level,
            "color": self.color,
            "timestamp": self.timestamp,
            "fixation_rate": self.fixation_rate,
            "avg_fixation_duration": self.avg_fixation_duration,
            "saccade_velocity": self.saccade_velocity,
            "pupil_dilation": self.pupil_dilation
        }