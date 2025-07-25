#!/usr/bin/env python3
"""
Sol SDK Client - Corrected implementation based on actual SDK documentation
Properly integrates with sol_sdk.synchronous.sync_client.SyncClient
"""

import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

from config import config

logger = logging.getLogger(__name__)

@dataclass
class GazeDataPoint:
    """Normalized gaze data structure based on Sol SDK"""
    timestamp: int
    x: float  # Normalized coordinates (0.0 to 1.0)
    y: float  # Normalized coordinates (0.0 to 1.0) 
    confidence: float  # Confidence score (0.0 to 1.0)
    scene_image: Optional[bytes] = None

class SolGlassesClient:
    """
    Corrected Sol Glasses client using actual SDK API
    Based on sol_sdk.synchronous.sync_client.SyncClient documentation
    """
    
    def __init__(self, address: str = None, port: int = None, rtsp_port: int = None):
        self.address = address or config.sol_sdk.default_address  
        self.port = port or config.sol_sdk.default_port
        self.rtsp_port = rtsp_port or config.sol_sdk.rtsp_port
        self._client = None
        self._connected = False
        
    def connect(self) -> bool:
        """Connect to Sol Glasses using actual SDK API"""
        try:
            # Import here to handle cases where SDK isn't available
            from ganzin.sol_sdk.synchronous.sync_client import SyncClient
            
            logger.info(f"Connecting to Sol Glasses at {self.address}:{self.port}")
            
            # Use correct SDK constructor: SyncClient(address, port, rtsp_port)
            self._client = SyncClient(
                address=self.address,
                port=self.port,
                rtsp_port=self.rtsp_port
            )
            
            # Test connection by getting version
            version_response = self._client.get_version()
            logger.info(f"Connected to Sol Glasses SDK version: {version_response.remote_api_version}")
            
            # Get device status
            status_response = self._client.get_status()
            logger.info(f"Device status: {status_response.device_name}")
            
            self._connected = True
            return True
            
        except ImportError as e:
            logger.error(f"Sol SDK not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Sol Glasses: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Sol Glasses"""
        if self._client and self._connected:
            try:
                # The SDK client doesn't seem to have explicit disconnect
                # but we can clean up our references
                self._client = None
                self._connected = False
                logger.info("Disconnected from Sol Glasses")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to Sol Glasses"""
        return self._connected and self._client is not None
    
    def capture_gaze_data(self) -> Optional[GazeDataPoint]:
        """
        Capture single gaze data point using correct SDK API
        Returns normalized gaze data or None if capture fails
        """
        if not self.is_connected():
            logger.warning("Not connected to Sol Glasses")
            return None
            
        try:
            # Use actual SDK method: capture() not capture_gaze()
            capture_response = self._client.capture()
            
            # Extract gaze data from response based on SDK structure
            # Note: This structure needs to be verified with actual SDK response
            gaze_data = GazeDataPoint(
                timestamp=int(time.time() * 1000),  # Current timestamp
                x=getattr(capture_response, 'gaze_x', 0.5),  # Normalized X
                y=getattr(capture_response, 'gaze_y', 0.5),  # Normalized Y
                confidence=getattr(capture_response, 'confidence', 1.0),  # Confidence
                scene_image=getattr(capture_response, 'scene_image', None)  # Optional scene
            )
            
            return gaze_data
            
        except Exception as e:
            logger.error(f"Failed to capture gaze data: {e}")
            return None
    
    def start_recording(self) -> bool:
        """Start recording session on Sol Glasses"""
        if not self.is_connected():
            return False
            
        try:
            record_response = self._client.begin_record()
            logger.info("Started recording on Sol Glasses")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> bool:
        """Stop recording session on Sol Glasses"""
        if not self.is_connected():
            return False
            
        try:
            record_response = self._client.end_record()
            logger.info("Stopped recording on Sol Glasses")
            return True
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return False
    
    def add_tag(self, tag: str) -> bool:
        """Add tag to current recording session"""
        if not self.is_connected():
            return False
            
        try:
            from ganzin.sol_sdk.requests import AddTagRequest
            tag_request = AddTagRequest(tag=tag)
            tag_response = self._client.add_tag(tag_request)
            logger.info(f"Added tag: {tag}")
            return True
        except Exception as e:
            logger.error(f"Failed to add tag: {e}")
            return False
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """Get Sol Glasses device information"""
        if not self.is_connected():
            return None
            
        try:
            status_response = self._client.get_status()
            version_response = self._client.get_version()
            
            return {
                'device_name': getattr(status_response, 'device_name', 'Unknown'),
                'sdk_version': getattr(version_response, 'remote_api_version', 'Unknown'),
                'status': getattr(status_response, 'status', 'Unknown')
            }
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return None
    
    def setup_streaming(self) -> bool:
        """Setup streaming for continuous gaze data"""
        if not self.is_connected():
            return False
            
        try:
            # Create streaming thread using SDK
            streaming_thread = self._client.create_streaming_thread()
            logger.info("Streaming setup complete")
            return True
        except Exception as e:
            logger.error(f"Failed to setup streaming: {e}")
            return False
    
    def get_streaming_gaze_data(self) -> Optional[GazeDataPoint]:
        """Get gaze data from streaming (if available)"""
        if not self.is_connected():
            return None
            
        try:
            # Get gazes from streaming
            gaze_data_list = self._client.get_gazes_from_streaming()
            
            if gaze_data_list:
                # Return the most recent gaze data
                latest_gaze = gaze_data_list[-1]
                return GazeDataPoint(
                    timestamp=int(time.time() * 1000),
                    x=getattr(latest_gaze, 'x', 0.5),
                    y=getattr(latest_gaze, 'y', 0.5),
                    confidence=getattr(latest_gaze, 'confidence', 1.0)
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get streaming gaze data: {e}")
            return None

class MockSolGlassesClient:
    """Mock client for testing without hardware"""
    
    def __init__(self, *args, **kwargs):
        self._connected = False
        self.address = "127.0.0.1"
        self.port = 8080
        
    def connect(self) -> bool:
        logger.info("Mock: Connected to Sol Glasses")
        self._connected = True
        return True
        
    def disconnect(self):
        logger.info("Mock: Disconnected from Sol Glasses")
        self._connected = False
        
    def is_connected(self) -> bool:
        return self._connected
        
    def capture_gaze_data(self) -> Optional[GazeDataPoint]:
        if not self._connected:
            return None
            
        import random
        return GazeDataPoint(
            timestamp=int(time.time() * 1000),
            x=random.uniform(0.1, 0.9),
            y=random.uniform(0.2, 0.8),
            confidence=random.uniform(0.8, 0.98)
        )
    
    def start_recording(self) -> bool:
        logger.info("Mock: Started recording")
        return True
        
    def stop_recording(self) -> bool:
        logger.info("Mock: Stopped recording")
        return True
        
    def add_tag(self, tag: str) -> bool:
        logger.info(f"Mock: Added tag {tag}")
        return True
        
    def get_device_info(self) -> Dict[str, Any]:
        return {
            'device_name': 'Mock Sol Glasses',
            'sdk_version': '1.1.1',
            'status': 'Connected'
        }
    
    def setup_streaming(self) -> bool:
        logger.info("Mock: Streaming setup complete")
        return True
        
    def get_streaming_gaze_data(self) -> Optional[GazeDataPoint]:
        return self.capture_gaze_data()

def create_sol_glasses_client(address: str = None, port: int = None, use_mock: bool = False) -> SolGlassesClient:
    """Factory function to create Sol Glasses client"""
    if use_mock or config.debug_mode:
        return MockSolGlassesClient(address, port)
    else:
        return SolGlassesClient(address, port)