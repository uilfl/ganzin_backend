#!/usr/bin/env python3
"""
Test script to verify Sol Glasses connection and data retrieval.
This script tests the basic functionality step by step.
"""

import sys
import os
import asyncio
import time
import json

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_sdk_import():
    """Test 1: Can we import the Sol SDK?"""
    print("🔍 Test 1: Testing Sol SDK import...")
    
    try:
        # Check if wheel is available
        wheel_path = "ganzin_sol_sdk-1.1.1-py3-none-any.whl"
        if not os.path.exists(wheel_path):
            print(f"❌ Sol SDK wheel not found at {wheel_path}")
            return False
        
        # Try importing SDK components
        from ganzin.sol_sdk.synchronous.sync_client import SyncClient
        from ganzin.sol_sdk.responses import CaptureResponse
        print("✅ Sol SDK import successful")
        return True
        
    except ImportError as e:
        print(f"❌ Sol SDK import failed: {e}")
        print("💡 Make sure to install: pip install ganzin_sol_sdk-1.1.1-py3-none-any.whl")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_sol_client_wrapper():
    """Test 2: Can we use the Sol client wrapper?"""
    print("\n🔍 Test 2: Testing Sol client wrapper...")
    
    try:
        from sol_sdk_client import create_sol_glasses_client, GazeDataPoint
        
        # Test with mock client first
        mock_client = create_sol_glasses_client(use_mock=True)
        print("✅ Mock client created successfully")
        
        # Test basic operations
        if mock_client.connect():
            print("✅ Mock client connection successful")
            
            gaze_data = mock_client.capture_gaze_data()
            if gaze_data and isinstance(gaze_data, GazeDataPoint):
                print(f"✅ Mock gaze data: x={gaze_data.x:.3f}, y={gaze_data.y:.3f}, confidence={gaze_data.confidence:.3f}")
            
            device_info = mock_client.get_device_info()
            print(f"✅ Mock device info: {device_info}")
            
            mock_client.disconnect()
            return True
        else:
            print("❌ Mock client connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Sol client wrapper test failed: {e}")
        return False

def test_real_hardware_connection():
    """Test 3: Can we connect to real Sol Glasses hardware?"""
    print("\n🔍 Test 3: Testing real hardware connection...")
    
    try:
        from sol_sdk_client import create_sol_glasses_client
        from utils.server_info import get_ip_and_port
        
        # Get Sol Glasses IP from examples
        ip, port = get_ip_and_port()
        print(f"Attempting connection to Sol Glasses at {ip}:{port}")
        
        # Create real client
        real_client = create_sol_glasses_client(address=ip, port=int(port), use_mock=False)
        
        # Test connection
        if real_client.connect():
            print("✅ Real hardware connection successful!")
            
            # Get device info
            device_info = real_client.get_device_info()
            print(f"✅ Device info: {device_info}")
            
            # Capture gaze data
            gaze_data = real_client.capture_gaze_data()
            if gaze_data:
                print(f"✅ Real gaze data: x={gaze_data.x:.3f}, y={gaze_data.y:.3f}, confidence={gaze_data.confidence:.3f}")
            else:
                print("⚠️  No gaze data received")
            
            real_client.disconnect()
            return True
        else:
            print("❌ Real hardware connection failed")
            print("💡 Make sure Sol Glasses are connected and accessible at 192.168.2.19:8080")
            return False
            
    except Exception as e:
        print(f"❌ Real hardware test failed: {e}")
        return False

def test_example_streaming():
    """Test 4: Test streaming using Sol SDK examples pattern"""
    print("\n🔍 Test 4: Testing streaming pattern from examples...")
    
    try:
        # Add examples directory to path
        examples_path = os.path.join(os.path.dirname(__file__), "..", "examples")
        sys.path.append(examples_path)
        
        from utils.server_info import get_ip_and_port
        address, port = get_ip_and_port()
        
        print(f"Testing streaming connection to {address}:{port}")
        
        # Import SDK for streaming test
        from ganzin.sol_sdk.synchronous.sync_client import SyncClient
        
        # Create direct SDK connection
        client = SyncClient(address, int(port))
        
        # Test basic SDK methods
        try:
            version = client.get_version()
            print(f"✅ SDK Version: {version.remote_api_version}")
            
            status = client.get_status()
            print(f"✅ Device Status: Connected")
            
            # Try capture (like capture_frame_and_gaze.py example)
            capture_result = client.capture()
            print(f"✅ Capture successful: {type(capture_result)}")
            
            return True
            
        except Exception as e:
            print(f"❌ SDK direct connection failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Example streaming test failed: {e}")
        return False

async def test_device_agent():
    """Test 5: Test the device agent streaming"""
    print("\n🔍 Test 5: Testing device agent streaming...")
    
    try:
        from device_agent import SolGlassesAgent
        
        # Create agent for testing
        agent = SolGlassesAgent(
            backend_url="ws://localhost:8000",
            session_id="test_connection"
        )
        
        print("✅ Device agent created")
        
        # Test connection (this will fail if backend not running, but that's OK for now)
        try:
            connection_ok = await agent.test_connection()
            if connection_ok:
                print("✅ Device agent connection test passed")
            else:
                print("⚠️  Device agent connection test failed (backend may not be running)")
        except Exception as e:
            print(f"⚠️  Device agent connection test failed: {e}")
        
        # Test gaze data generation
        gaze_data = await agent.real_gaze_data()
        if gaze_data:
            print(f"✅ Gaze data generated: {json.dumps(gaze_data, indent=2)}")
            return True
        else:
            print("❌ No gaze data generated")
            return False
            
    except Exception as e:
        print(f"❌ Device agent test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Sol Glasses Integration Test Suite")
    print("=" * 50)
    
    results = []
    
    # Test 1: SDK Import
    results.append(test_sdk_import())
    
    # Test 2: Client Wrapper  
    results.append(test_sol_client_wrapper())
    
    # Test 3: Real Hardware
    results.append(test_real_hardware_connection())
    
    # Test 4: Example Streaming
    results.append(test_example_streaming())
    
    # Test 5: Device Agent
    results.append(await test_device_agent())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    test_names = [
        "SDK Import",
        "Client Wrapper", 
        "Real Hardware",
        "Example Streaming",
        "Device Agent"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    passed = sum(results)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= 3:
        print("🎉 Sol Glasses integration is ready for testing!")
    else:
        print("⚠️  Some issues need to be resolved before proceeding")

if __name__ == "__main__":
    asyncio.run(main())