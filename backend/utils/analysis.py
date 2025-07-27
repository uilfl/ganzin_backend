#!/usr/bin/env python3
"""
Analysis utilities for gaze data and AOI interactions
Following project_structure.md guidance for basic statistics
"""

import numpy as np
from typing import Dict, List, Any, Tuple
import time

def calculate_aoi_statistics(hit_logs: List[Dict]) -> Dict[str, Any]:
    """
    Calculate basic AOI statistics
    
    Args:
        hit_logs: List of hit log dictionaries
    
    Returns:
        Dictionary with AOI statistics
    """
    if not hit_logs:
        return {}
    
    aoi_stats = {}
    
    for hit in hit_logs:
        aoi_id = hit.get("aoi_id", "unknown")
        
        if aoi_id not in aoi_stats:
            aoi_stats[aoi_id] = {
                "hit_count": 0,
                "total_fixation_time": 0.0,
                "fixation_durations": [],
                "confidences": [],
                "is_vocabulary": hit.get("is_vocabulary_word", False),
                "text": hit.get("aoi_text", "")
            }
        
        stats = aoi_stats[aoi_id]  
        stats["hit_count"] += 1
        stats["total_fixation_time"] += hit.get("fixation_duration", 0.0)
        stats["fixation_durations"].append(hit.get("fixation_duration", 0.0))
        stats["confidences"].append(hit.get("confidence", 0.0))
    
    # Calculate summary statistics
    for aoi_id, stats in aoi_stats.items():
        if stats["fixation_durations"]:
            stats["avg_fixation_duration"] = np.mean(stats["fixation_durations"])
            stats["max_fixation_duration"] = np.max(stats["fixation_durations"])
        
        if stats["confidences"]:
            stats["avg_confidence"] = np.mean(stats["confidences"])
    
    return aoi_stats

def analyze_gaze_patterns(gaze_trail: List[Dict]) -> Dict[str, Any]:
    """
    Analyze gaze movement patterns
    
    Args:
        gaze_trail: List of gaze point dictionaries
    
    Returns:
        Dictionary with pattern analysis
    """
    if len(gaze_trail) < 2:
        return {}
    
    # Extract coordinates
    x_coords = [g.get("gaze_pos_x", 0) for g in gaze_trail]
    y_coords = [g.get("gaze_pos_y", 0) for g in gaze_trail]
    timestamps = [g.get("timestamp", 0) for g in gaze_trail]
    
    # Calculate velocities
    velocities = []
    for i in range(1, len(gaze_trail)):
        dx = x_coords[i] - x_coords[i-1]
        dy = y_coords[i] - y_coords[i-1]
        dt = timestamps[i] - timestamps[i-1]
        
        if dt > 0:
            velocity = np.sqrt(dx*dx + dy*dy) / dt
            velocities.append(velocity)
    
    return {
        "total_samples": len(gaze_trail),
        "duration_seconds": timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0,
        "gaze_range": {
            "x_min": min(x_coords),
            "x_max": max(x_coords), 
            "y_min": min(y_coords),
            "y_max": max(y_coords)
        },
        "velocities": {
            "mean": np.mean(velocities) if velocities else 0,
            "max": np.max(velocities) if velocities else 0,
            "std": np.std(velocities) if velocities else 0
        }
    }