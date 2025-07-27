#!/usr/bin/env python3
"""
Export utilities for session data analysis
Following project_structure.md guidance for data export
"""

import json
import os
import time
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import asdict

def export_session(manager, session_id: str, output_dir: str = "data") -> str:
    """
    Export session data to JSON
    Following project_structure.md export pattern
    
    Args:
        manager: GazeDataManager instance
        session_id: Session identifier
        output_dir: Output directory for files
    
    Returns:
        Filename of exported data
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Gather all session data
    session_data = {
        "session_id": session_id,
        "export_timestamp": time.time(),
        "gaze_trail": [asdict(g) for g in manager.gaze_trail],
        "aois": {k: asdict(v) for k, v in manager.aoi_collection.elements.items()},
        "hit_log": [asdict(h) for h in manager.hit_log_manager.hits] if manager.hit_log_manager else [],
        "performance": manager.performance_stats,
        "calibration": manager.calibration_transform
    }
    
    # Generate filename
    timestamp = int(time.time())
    filename = os.path.join(output_dir, f"{session_id}_{timestamp}.json")
    
    # Export to JSON
    with open(filename, 'w') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    return filename

def export_to_pandas(session_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """
    Convert session data to pandas DataFrames for analysis
    
    Args:
        session_data: Exported session data dictionary
    
    Returns:
        Dictionary of DataFrames for different data types
    """
    dataframes = {}
    
    # Gaze trail DataFrame
    if session_data.get("gaze_trail"):
        dataframes["gaze_trail"] = pd.DataFrame(session_data["gaze_trail"])
    
    # Hit log DataFrame  
    if session_data.get("hit_log"):
        dataframes["hit_log"] = pd.DataFrame(session_data["hit_log"])
    
    # AOI DataFrame
    if session_data.get("aois"):
        aoi_list = list(session_data["aois"].values())
        if aoi_list:
            dataframes["aois"] = pd.DataFrame(aoi_list)
    
    return dataframes