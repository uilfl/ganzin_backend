#!/usr/bin/env python3
"""
Hit Log data model for tracking AOI interactions
Based on vocabulary discovery and gaze analysis testing
"""

from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import time

@dataclass
class HitLog:
    """
    Records when gaze hits an Area of Interest (AOI)
    Based on frontend integration testing and vocabulary discovery insights
    """
    # Basic Hit Information
    gaze_timestamp: float  # When the gaze hit occurred (Unix timestamp)
    aoi_id: str  # ID of the AOI that was hit
    hit_type: str  # "2d", "3d", or "both"
    
    # Gaze Details
    gaze_x: float  # Gaze X coordinate at hit time
    gaze_y: float  # Gaze Y coordinate at hit time
    confidence: float  # Gaze confidence (0.0-1.0)
    
    # AOI Context
    aoi_text: str  # Text content of the hit AOI
    aoi_center_x: float  # AOI center X coordinate
    aoi_center_y: float  # AOI center Y coordinate
    
    # Interaction Metrics
    fixation_duration: float = 0.0  # How long gaze stayed in AOI (seconds)
    entry_velocity: float = 0.0  # Saccade velocity when entering AOI
    is_vocabulary_word: bool = False  # Whether this was a vocabulary target
    
    # Session Context  
    session_id: Optional[str] = None  # Associated session ID
    sequence_number: int = 0  # Hit order within session
    
    # Analysis Metadata
    created_at: float = None  # Log creation timestamp
    cognitive_load_score: Optional[float] = None  # Cognitive load at hit time
    
    def __post_init__(self):
        """Initialize default values after creation"""
        if self.created_at is None:
            self.created_at = time.time()
    
    @classmethod
    def create_from_gaze_and_aoi(cls, gaze_point, aoi_element, hit_type: str = "2d", 
                                session_id: Optional[str] = None) -> 'HitLog':
        """
        Create hit log from gaze point and AOI element
        
        Args:
            gaze_point: GazePoint instance
            aoi_element: AOIElement instance  
            hit_type: Type of hit detection used
            session_id: Associated session ID
        
        Returns:
            HitLog instance
        """
        aoi_center_x, aoi_center_y = aoi_element.get_center_point()
        
        return cls(
            gaze_timestamp=gaze_point.timestamp,
            aoi_id=aoi_element.id,
            hit_type=hit_type,
            gaze_x=gaze_point.calibrated_x or gaze_point.gaze_pos_x,
            gaze_y=gaze_point.calibrated_y or gaze_point.gaze_pos_y,
            confidence=gaze_point.confidence,
            aoi_text=aoi_element.text,
            aoi_center_x=aoi_center_x,
            aoi_center_y=aoi_center_y,
            is_vocabulary_word=aoi_element.vocabulary_word,
            session_id=session_id
        )
    
    def calculate_distance_from_center(self) -> float:
        """
        Calculate distance between gaze point and AOI center
        
        Returns:
            Distance in pixels
        """
        dx = self.gaze_x - self.aoi_center_x
        dy = self.gaze_y - self.aoi_center_y
        return (dx * dx + dy * dy) ** 0.5
    
    def is_precise_hit(self, threshold: float = 20.0) -> bool:
        """
        Check if this was a precise hit (close to AOI center)
        
        Args:
            threshold: Maximum distance for "precise" classification
        
        Returns:
            True if hit was within threshold distance of center
        """
        return self.calculate_distance_from_center() <= threshold
    
    def is_long_fixation(self, threshold: float = 1.5) -> bool:
        """
        Check if this hit involved a long fixation
        
        Args:
            threshold: Minimum duration for "long" classification (seconds)
        
        Returns:
            True if fixation was longer than threshold
        """
        return self.fixation_duration >= threshold
    
    def get_hit_quality(self) -> str:
        """
        Assess the quality of this hit based on multiple factors
        
        Returns:
            Quality rating: "excellent", "good", "fair", "poor"
        """
        distance = self.calculate_distance_from_center()
        
        if (self.confidence >= 0.8 and 
            distance <= 15.0 and 
            self.fixation_duration >= 1.0):
            return "excellent"
        elif (self.confidence >= 0.6 and 
              distance <= 25.0 and 
              self.fixation_duration >= 0.5):
            return "good"
        elif (self.confidence >= 0.4 and 
              distance <= 40.0):
            return "fair"
        else:
            return "poor"
    
    def to_frontend_format(self) -> dict:
        """
        Convert to frontend-compatible format for visualization
        
        Returns:
            Dictionary suitable for frontend hit visualization
        """
        return {
            "timestamp": int(self.gaze_timestamp * 1000),  # Convert to milliseconds
            "aoi_id": self.aoi_id,
            "aoi_text": self.aoi_text,
            "gaze_position": {"x": self.gaze_x, "y": self.gaze_y},
            "aoi_center": {"x": self.aoi_center_x, "y": self.aoi_center_y},
            "fixation_duration": self.fixation_duration,
            "confidence": self.confidence,
            "is_vocabulary": self.is_vocabulary_word,
            "hit_quality": self.get_hit_quality(),
            "distance_from_center": self.calculate_distance_from_center()
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class HitLogManager:
    """
    Manager for collecting and analyzing hit logs
    Based on vocabulary discovery testing and gaze pattern analysis
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id
        self.hits: List[HitLog] = []
        self.current_fixations: Dict[str, Dict] = {}  # Track ongoing fixations
        self.sequence_counter = 0
    
    def add_hit(self, hit_log: HitLog) -> None:
        """
        Add a hit log entry
        
        Args:
            hit_log: HitLog instance to add
        """
        # Set sequence number and session ID
        self.sequence_counter += 1
        hit_log.sequence_number = self.sequence_counter
        if self.session_id:
            hit_log.session_id = self.session_id
        
        self.hits.append(hit_log)
    
    def start_fixation(self, aoi_id: str, gaze_point, aoi_element) -> None:
        """
        Start tracking a fixation on an AOI
        
        Args:
            aoi_id: AOI identifier
            gaze_point: Current gaze point
            aoi_element: AOI element being fixated
        """
        self.current_fixations[aoi_id] = {
            "start_time": gaze_point.timestamp,
            "start_gaze": gaze_point,
            "aoi_element": aoi_element,
            "gaze_points": [gaze_point]
        }
    
    def update_fixation(self, aoi_id: str, gaze_point) -> None:
        """
        Update ongoing fixation with new gaze point
        
        Args:
            aoi_id: AOI identifier
            gaze_point: Current gaze point
        """
        if aoi_id in self.current_fixations:
            self.current_fixations[aoi_id]["gaze_points"].append(gaze_point)
    
    def end_fixation(self, aoi_id: str, final_gaze_point) -> Optional[HitLog]:
        """
        End fixation tracking and create hit log
        
        Args:
            aoi_id: AOI identifier
            final_gaze_point: Final gaze point in fixation
        
        Returns:
            HitLog if fixation was significant, None otherwise
        """
        if aoi_id not in self.current_fixations:
            return None
        
        fixation_data = self.current_fixations.pop(aoi_id)
        start_time = fixation_data["start_time"]
        duration = final_gaze_point.timestamp - start_time
        
        # Only log fixations longer than minimum threshold (200ms)
        if duration < 0.2:
            return None
        
        # Calculate average gaze position during fixation
        gaze_points = fixation_data["gaze_points"]
        avg_x = sum(gp.gaze_pos_x for gp in gaze_points) / len(gaze_points)
        avg_y = sum(gp.gaze_pos_y for gp in gaze_points) / len(gaze_points)
        avg_confidence = sum(gp.confidence for gp in gaze_points) / len(gaze_points)
        
        # Create hit log with fixation details
        aoi_element = fixation_data["aoi_element"]
        aoi_center_x, aoi_center_y = aoi_element.get_center_point()
        
        hit_log = HitLog(
            gaze_timestamp=start_time,
            aoi_id=aoi_id,
            hit_type="fixation",
            gaze_x=avg_x,
            gaze_y=avg_y,
            confidence=avg_confidence,
            aoi_text=aoi_element.text,
            aoi_center_x=aoi_center_x,
            aoi_center_y=aoi_center_y,
            fixation_duration=duration,
            is_vocabulary_word=aoi_element.vocabulary_word,
            session_id=self.session_id
        )
        
        self.add_hit(hit_log)
        return hit_log
    
    def get_vocabulary_hits(self) -> List[HitLog]:
        """Get all hits on vocabulary words"""
        return [hit for hit in self.hits if hit.is_vocabulary_word]
    
    def get_long_fixations(self, threshold: float = 1.5) -> List[HitLog]:
        """Get all hits with long fixations"""
        return [hit for hit in self.hits if hit.is_long_fixation(threshold)]
    
    def get_aoi_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for each AOI
        
        Returns:
            Dictionary with AOI statistics
        """
        aoi_stats = {}
        
        for hit in self.hits:
            aoi_id = hit.aoi_id
            if aoi_id not in aoi_stats:
                aoi_stats[aoi_id] = {
                    "hit_count": 0,
                    "total_fixation_time": 0.0,
                    "average_confidence": 0.0,
                    "vocabulary_word": hit.is_vocabulary_word,
                    "text": hit.aoi_text,
                    "hit_qualities": []
                }
            
            stats = aoi_stats[aoi_id]
            stats["hit_count"] += 1
            stats["total_fixation_time"] += hit.fixation_duration
            stats["average_confidence"] += hit.confidence
            stats["hit_qualities"].append(hit.get_hit_quality())
        
        # Calculate averages
        for aoi_id, stats in aoi_stats.items():
            if stats["hit_count"] > 0:
                stats["average_confidence"] /= stats["hit_count"]
                stats["average_fixation_duration"] = stats["total_fixation_time"] / stats["hit_count"]
        
        return aoi_stats
    
    def to_frontend_format(self) -> List[dict]:
        """Convert all hits to frontend format"""
        return [hit.to_frontend_format() for hit in self.hits]
    
    def export_session_data(self) -> dict:
        """
        Export complete hit log data for session analysis
        
        Returns:
            Comprehensive session hit data
        """
        return {
            "session_id": self.session_id,
            "total_hits": len(self.hits),
            "vocabulary_hits": len(self.get_vocabulary_hits()),
            "long_fixations": len(self.get_long_fixations()),
            "aoi_statistics": self.get_aoi_statistics(),
            "hit_logs": [hit.to_dict() for hit in self.hits],
            "export_timestamp": time.time()
        }