#!/usr/bin/env python3
"""
Debug script to understand the capture API response format
"""

import sys
import os
import json

# Add examples path
examples_path = os.path.join(os.path.dirname(__file__), "..", "examples")
sys.path.append(examples_path)

def debug_capture_response():
    """Debug the actual capture API response structure"""
    print("🔍 Debugging Sol SDK capture response...")
    
    try:
        from utils.server_info import get_ip_and_port
        from ganzin.sol_sdk.synchronous.sync_client import SyncClient
        from ganzin.sol_sdk.responses import CaptureResponse
        
        address, port = get_ip_and_port()
        print(f"Connecting to {address}:{port}")
        
        client = SyncClient(address, int(port))
        
        # Get version info
        version = client.get_version()
        print(f"SDK Version: {version.remote_api_version}")
        
        # Try capture
        print("\n📡 Attempting capture...")
        capture_response = client.capture()
        
        print(f"Response type: {type(capture_response)}")
        print(f"Response attributes: {dir(capture_response)}")
        
        # Try to understand response structure
        if hasattr(capture_response, 'result'):
            print(f"Has result attribute: {type(capture_response.result)}")
            try:
                result = CaptureResponse.from_raw(capture_response.result)
                print(f"CaptureResponse.from_raw succeeded: {type(result)}")
                print(f"Result attributes: {dir(result)}")
                
                if hasattr(result, 'gaze_data'):
                    print(f"Gaze data: {result.gaze_data}")
                if hasattr(result, 'timestamp'):
                    print(f"Timestamp: {result.timestamp}")
                    
            except Exception as e:
                print(f"CaptureResponse.from_raw failed: {e}")
                
                # Try raw access
                print(f"Raw result: {capture_response.result}")
                
        # Try direct attribute access
        for attr in ['gaze_data', 'timestamp', 'scene_image', 'combined', 'gaze_2d']:
            if hasattr(capture_response, attr):
                val = getattr(capture_response, attr)
                print(f"Direct access {attr}: {type(val)} = {val}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_streaming_gaze():
    """Debug streaming gaze data structure"""
    print("\n🔍 Debugging streaming gaze data...")
    
    try:
        from utils.server_info import get_ip_and_port
        from ganzin.sol_sdk.synchronous.sync_client import SyncClient
        from ganzin.sol_sdk.synchronous.models import StreamingMode
        
        address, port = get_ip_and_port()
        client = SyncClient(address, int(port))
        
        # Start streaming
        print("Starting streaming thread...")
        thread = client.create_streaming_thread(StreamingMode.GAZE)
        thread.start()
        
        # Get some gaze data
        print("Getting gaze data from streaming...")
        gazes = client.get_gazes_from_streaming(timeout=5.0)
        
        if gazes:
            print(f"Got {len(gazes)} gaze samples")
            first_gaze = gazes[0]
            print(f"First gaze type: {type(first_gaze)}")
            print(f"First gaze attributes: {dir(first_gaze)}")
            
            # Check for common attributes
            for attr in ['combined', 'gaze_2d', 'x', 'y', 'timestamp']:
                if hasattr(first_gaze, attr):
                    val = getattr(first_gaze, attr)
                    print(f"Gaze.{attr}: {type(val)} = {val}")
                    
                    # If it's an object, check its attributes too
                    if hasattr(val, '__dict__') or hasattr(val, '__slots__'):
                        print(f"  {attr} sub-attributes: {dir(val)}")
                        if hasattr(val, 'x') and hasattr(val, 'y'):
                            print(f"  {attr}.x = {getattr(val, 'x')}")
                            print(f"  {attr}.y = {getattr(val, 'y')}")
        else:
            print("No gaze data received from streaming")
            
        thread.stop()
        return True
        
    except Exception as e:
        print(f"❌ Streaming debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Sol SDK Response Structure Debug")
    print("=" * 50)
    
    debug_capture_response()
    debug_streaming_gaze()
    
    print("\n💡 Use this info to fix capture API in sol_sdk_client.py")