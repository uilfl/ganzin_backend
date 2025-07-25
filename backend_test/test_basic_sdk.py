#!/usr/bin/env python3
"""
Basic Sol SDK Connection Test
Tests the fundamental SDK functionality step by step.
"""

import sys
import os
import time

# Add examples path for server_info
examples_path = os.path.join(os.path.dirname(__file__), "..", "examples")
sys.path.append(examples_path)

def test_sdk_import():
    """Test if Sol SDK can be imported"""
    print("🔍 Testing Sol SDK import...")
    
    try:
        from ganzin.sol_sdk.synchronous.sync_client import SyncClient
        from ganzin.sol_sdk.responses import CaptureResponse
        from ganzin.sol_sdk.requests import AddTagRequest
        print("✅ Sol SDK imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Sol SDK import failed: {e}")
        return False

def test_hardware_connection():
    """Test connection to Sol Glasses hardware"""
    print("\n🔍 Testing hardware connection...")
    
    try:
        from utils.server_info import get_ip_and_port
        from ganzin.sol_sdk.synchronous.sync_client import SyncClient
        
        address, port = get_ip_and_port()
        print(f"Connecting to Sol Glasses at {address}:{port}")
        
        # Create client
        client = SyncClient(address, int(port))
        
        # Test version
        version = client.get_version()
        print(f"✅ Connected! SDK Version: {version.remote_api_version}")
        
        # Test status
        status = client.get_status()
        print(f"✅ Device Status: {status.device_name}")
        
        return True, client
        
    except Exception as e:
        print(f"❌ Hardware connection failed: {e}")
        print("💡 Make sure Sol Glasses are connected and accessible")
        return False, None

def test_capture_gaze(client):
    """Test capturing gaze data"""
    print("\n🔍 Testing gaze data capture...")
    
    if not client:
        print("❌ No client available for testing")
        return False
    
    try:
        # Capture frame and gaze (like the example)
        capture_result = client.capture()
        print(f"✅ Capture successful: {type(capture_result)}")
        
        # Try to extract gaze data
        # Note: This structure needs verification with actual hardware
        print(f"✅ Capture result received")
        return True
        
    except Exception as e:
        print(f"❌ Gaze capture failed: {e}")
        return False

def test_recording(client):
    """Test recording functionality"""
    print("\n🔍 Testing recording functionality...")
    
    if not client:
        print("❌ No client available for testing")
        return False
    
    try:
        # Start recording
        client.begin_record()
        print("✅ Recording started")
        
        # Wait a moment
        time.sleep(2)
        
        # Add a tag
        from ganzin.sol_sdk.requests import AddTagRequest
        tag_request = AddTagRequest(tag="test_tag")
        client.add_tag(tag_request)
        print("✅ Tag added")
        
        # Stop recording
        client.end_record()
        print("✅ Recording stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Recording test failed: {e}")
        return False

def main():
    """Run basic SDK tests"""
    print("🚀 Basic Sol SDK Test")
    print("=" * 30)
    
    # Test 1: Import
    if not test_sdk_import():
        print("\n❌ Cannot proceed without SDK import")
        return
    
    # Test 2: Connection
    connected, client = test_hardware_connection()
    if not connected:
        print("\n⚠️  Hardware tests skipped (no connection)")
        return
    
    # Test 3: Capture
    test_capture_gaze(client)
    
    # Test 4: Recording
    test_recording(client)
    
    print("\n✅ Basic SDK test completed!")
    print("💡 If all tests passed, your Sol Glasses are ready for integration")

if __name__ == "__main__":
    main()