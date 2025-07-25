#!/usr/bin/env python3
"""
R4: Processing Service
Implements AOI mapping and gaze event detection (fixations/saccades)
≥95% detection precision requirement
"""

import asyncio
import json
import logging
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class GazeSample:
    """Gaze sample data structure"""
    timestamp: int
    x: float
    y: float
    confidence: float
    session_id: str

@dataclass
class GazeEvent:
    """Detected gaze event (fixation or saccade)"""
    event_type: str  # 'fixation' or 'saccade'
    start_ts: int
    end_ts: int
    duration_ms: int
    gaze_x: float
    gaze_y: float
    confidence: float
    aoi_id: Optional[str] = None

class FixationDetector:
    """
    R4: I-DT Fixation Detection Algorithm
    Window: 100ms, Dispersion threshold: 1° visual angle
    """
    
    def __init__(self, window_ms: int = 100, dispersion_threshold: float = 1.0):
        self.window_ms = window_ms
        self.dispersion_threshold = dispersion_threshold  # degrees
        self.sample_buffer = deque(maxlen=50)  # Keep last 50 samples
        
    def add_sample(self, sample: GazeSample) -> List[GazeEvent]:
        """Add sample and detect events"""
        self.sample_buffer.append(sample)
        return self._detect_events()
    
    def _detect_events(self) -> List[GazeEvent]:
        """Detect fixations and saccades using I-DT algorithm"""
        if len(self.sample_buffer) < 3:
            return []
        
        events = []
        samples = list(self.sample_buffer)
        
        # Find fixation candidates in sliding window
        for i in range(len(samples) - 2):
            window_samples = []
            start_time = samples[i].timestamp
            
            # Collect samples within time window
            for j in range(i, len(samples)):
                if samples[j].timestamp - start_time <= self.window_ms:
                    window_samples.append(samples[j])
                else:
                    break
            
            if len(window_samples) >= 3:
                dispersion = self._calculate_dispersion(window_samples)
                
                if dispersion <= self.dispersion_threshold:
                    # Fixation detected
                    fixation = self._create_fixation_event(window_samples)
                    if fixation:
                        events.append(fixation)
                else:
                    # Saccade detected (high dispersion)
                    saccade = self._create_saccade_event(window_samples)
                    if saccade:
                        events.append(saccade)
        
        return events
    
    def _calculate_dispersion(self, samples: List[GazeSample]) -> float:
        """Calculate spatial dispersion of gaze samples"""
        if len(samples) < 2:
            return 0.0
        
        x_coords = [s.x for s in samples]
        y_coords = [s.y for s in samples]
        
        # Calculate range (max - min)
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        
        # Convert pixel dispersion to degrees (approximate)
        # Assuming 1920x1080 screen at 60cm distance
        pixels_per_degree = 30  # Approximate conversion
        dispersion = math.sqrt(x_range**2 + y_range**2) / pixels_per_degree
        
        return dispersion
    
    def _create_fixation_event(self, samples: List[GazeSample]) -> Optional[GazeEvent]:
        """Create fixation event from samples"""
        if not samples:
            return None
        
        # Calculate centroid
        avg_x = sum(s.x for s in samples) / len(samples)
        avg_y = sum(s.y for s in samples) / len(samples)
        avg_confidence = sum(s.confidence for s in samples) / len(samples)
        
        return GazeEvent(
            event_type='fixation',
            start_ts=samples[0].timestamp,
            end_ts=samples[-1].timestamp,
            duration_ms=samples[-1].timestamp - samples[0].timestamp,
            gaze_x=avg_x,
            gaze_y=avg_y,
            confidence=avg_confidence
        )
    
    def _create_saccade_event(self, samples: List[GazeSample]) -> Optional[GazeEvent]:
        """Create saccade event from samples"""
        if len(samples) < 2:
            return None
        
        # Use start and end points for saccade
        start_sample = samples[0]
        end_sample = samples[-1]
        avg_confidence = sum(s.confidence for s in samples) / len(samples)
        
        return GazeEvent(
            event_type='saccade',
            start_ts=start_sample.timestamp,
            end_ts=end_sample.timestamp,
            duration_ms=end_sample.timestamp - start_sample.timestamp,
            gaze_x=(start_sample.x + end_sample.x) / 2,
            gaze_y=(start_sample.y + end_sample.y) / 2,
            confidence=avg_confidence
        )

class AOIMapper:
    """
    R4: Area of Interest (AOI) mapping using spatial indexing
    ≥99% gaze sample mapping accuracy
    """
    
    def __init__(self):
        self.aoi_cache = {}  # lesson_id -> AOI list
        
    async def load_aois(self, lesson_id: str, database):
        """Load AOI definitions for a lesson"""
        aois = await database.get_aois_for_lesson(lesson_id)
        self.aoi_cache[lesson_id] = aois
        logger.info(f"Loaded {len(aois)} AOIs for lesson {lesson_id}")
    
    def map_gaze_to_aoi(self, gaze_x: float, gaze_y: float, lesson_id: str) -> Optional[str]:
        """R4: Map gaze coordinates to AOI (pixel-perfect alignment)"""
        if lesson_id not in self.aoi_cache:
            return None
        
        aois = self.aoi_cache[lesson_id]
        
        # Simple point-in-rectangle test
        for aoi in aois:
            if (aoi['x'] <= gaze_x <= aoi['x'] + aoi['width'] and
                aoi['y'] <= gaze_y <= aoi['y'] + aoi['height']):
                return aoi['id']
        
        return None  # Gaze outside all AOIs

class ProcessingService:
    """
    R4: Main Processing Service
    Real-time gaze-to-AOI mapping and event detection
    """
    
    def __init__(self, database):
        self.database = database
        self.fixation_detector = FixationDetector()
        self.aoi_mapper = AOIMapper()
        self.active_sessions = {}  # session_id -> lesson_id
        
    async def start_session_processing(self, session_id: str, lesson_id: str):
        """Initialize processing for a new session"""
        self.active_sessions[session_id] = lesson_id
        await self.aoi_mapper.load_aois(lesson_id, self.database)
        logger.info(f"Started processing for session {session_id}, lesson {lesson_id}")
    
    async def process_gaze_sample(self, sample_data: dict) -> List[GazeEvent]:
        """
        R4: Process incoming gaze sample
        1. Map to AOI
        2. Detect fixation/saccade events
        3. Store events in database
        """
        try:
            # Parse sample data
            sample = GazeSample(
                timestamp=sample_data['timestamp'],
                x=sample_data['gaze_data']['x'],
                y=sample_data['gaze_data']['y'],
                confidence=sample_data['gaze_data']['confidence'],
                session_id=sample_data.get('session_id', 'unknown')
            )
            
            # Skip low-confidence samples
            if sample.confidence < 0.8:
                return []
            
            # Map gaze to AOI
            lesson_id = self.active_sessions.get(sample.session_id)
            if lesson_id:
                aoi_id = self.aoi_mapper.map_gaze_to_aoi(sample.x, sample.y, lesson_id)
            else:
                aoi_id = None
            
            # Detect gaze events
            events = self.fixation_detector.add_sample(sample)
            
            # Store events in database
            stored_events = []
            for event in events:
                event.aoi_id = aoi_id
                
                await self.database.insert_event(sample.session_id, {
                    'sample_ts': sample.timestamp,
                    'aoi_id': event.aoi_id,
                    'event_type': event.event_type,
                    'start_ts': event.start_ts,
                    'end_ts': event.end_ts,
                    'duration_ms': event.duration_ms,
                    'gaze_x': event.gaze_x,
                    'gaze_y': event.gaze_y,
                    'confidence': event.confidence
                })
                
                stored_events.append(event)
                
                logger.debug(f"Detected {event.event_type}: {event.duration_ms}ms at AOI {event.aoi_id}")
            
            return stored_events
            
        except Exception as e:
            logger.error(f"Error processing gaze sample: {e}")
            return []
    
    async def end_session_processing(self, session_id: str):
        """Clean up session processing"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        logger.info(f"Ended processing for session {session_id}")

# Simulated processing for testing
class MockProcessingService:
    """Mock processing service for testing without database"""
    
    def __init__(self):
        self.fixation_detector = FixationDetector()
        self.processed_count = 0
    
    async def process_gaze_sample(self, sample_data: dict) -> List[dict]:
        """Mock processing that returns simulated events"""
        self.processed_count += 1
        
        # Simulate occasional fixation detection
        if self.processed_count % 10 == 0:
            return [{
                'event_type': 'fixation',
                'duration_ms': 250,
                'aoi_id': f'word_{self.processed_count // 10}',
                'confidence': sample_data['gaze_data']['confidence']
            }]
        
        return []

# Global processing service instance
processing_service = None

async def init_processing_service(database):
    """Initialize processing service"""
    global processing_service
    processing_service = ProcessingService(database)
    logger.info("Processing service initialized")

def get_processing_service():
    """Get processing service instance"""
    return processing_service or MockProcessingService()