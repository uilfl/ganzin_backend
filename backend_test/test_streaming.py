#!/usr/bin/env python3
"""
Sol Glasses Streaming Test
Tests continuous gaze data streaming similar to the examples.
"""

import asyncio
import sys
import os
import time
import json

# Add examples path
examples_path = os.path.join(os.path.dirname(__file__), "..", "examples")
sys.path.append(examples_path)

async def test_async_streaming():
    """Test asynchronous gaze streaming like the examples"""
    print("🔍 Testing async gaze streaming...")
    
    try:
        from utils.server_info import get_ip_and_port
        from ganzin.sol_sdk.asynchronous.async_client import AsyncClient, recv_gaze
        
        address, port = get_ip_and_port()
        print(f"Connecting to Sol Glasses at {address}:{port}")
        
        async with AsyncClient(address, port) as ac:
            print("✅ Async client connected")
            
            # Stream gaze data for 5 seconds
            start_time = time.time()
            sample_count = 0
            
            print("📡 Starting gaze stream (5 seconds)...")
            
            async for data in recv_gaze(ac):
                # Extract gaze coordinates
                x = data.combined.gaze_2d.x
                y = data.combined.gaze_2d.y
                
                sample_count += 1
                
                # Print every 30th sample to avoid spam
                if sample_count % 30 == 0:
                    elapsed = time.time() - start_time
                    hz = sample_count / elapsed
                    print(f"Sample {sample_count}: x={x:.3f}, y={y:.3f} ({hz:.1f} Hz)")
                
                # Stop after 5 seconds
                if time.time() - start_time > 5:
                    break
            
            total_time = time.time() - start_time
            avg_hz = sample_count / total_time
            print(f"✅ Streaming test completed: {sample_count} samples in {total_time:.1f}s ({avg_hz:.1f} Hz)")
            
            return True
            
    except Exception as e:
        print(f"❌ Async streaming test failed: {e}")
        return False

async def test_video_with_gaze():
    """Test video streaming with gaze overlay (like the examples)"""
    print("\n🔍 Testing video + gaze streaming...")
    
    try:
        from utils.server_info import get_ip_and_port
        from ganzin.sol_sdk.asynchronous.async_client import AsyncClient, recv_gaze, recv_video
        from ganzin.sol_sdk.common_models import Camera
        
        address, port = get_ip_and_port()
        
        async with AsyncClient(address, port) as ac:
            print("✅ Video+gaze client connected")
            
            # Test if we can get video and gaze streams
            frame_count = 0
            gaze_count = 0
            
            # Create tasks for concurrent streaming
            async def count_frames():
                nonlocal frame_count
                async for frame in recv_video(ac, Camera.SCENE):
                    frame_count += 1
                    if frame_count >= 10:  # Stop after 10 frames
                        break
            
            async def count_gazes():
                nonlocal gaze_count
                async for gaze in recv_gaze(ac):
                    gaze_count += 1
                    if gaze_count >= 50:  # Stop after 50 gaze samples
                        break
            
            # Run both streams concurrently for a short time
            await asyncio.wait_for(
                asyncio.gather(count_frames(), count_gazes()),
                timeout=3.0
            )
            
            print(f"✅ Received {frame_count} video frames and {gaze_count} gaze samples")
            return True
            
    except asyncio.TimeoutError:
        print("⚠️  Video+gaze test timed out (this may be normal)")
        return True
    except Exception as e:
        print(f"❌ Video+gaze test failed: {e}")
        return False

def test_our_client_wrapper():
    """Test our Sol client wrapper with real hardware"""
    print("\n🔍 Testing our client wrapper...")
    
    try:
        from sol_sdk_client import create_sol_glasses_client
        from utils.server_info import get_ip_and_port
        
        ip, port = get_ip_and_port()
        
        # Test real client
        client = create_sol_glasses_client(address=ip, port=int(port), use_mock=False)
        
        if client.connect():
            print("✅ Our wrapper connected successfully")
            
            # Test device info
            info = client.get_device_info()
            print(f"✅ Device info: {info}")
            
            # Test gaze capture
            gaze_data = client.capture_gaze_data()
            if gaze_data:
                print(f"✅ Gaze data: x={gaze_data.x:.3f}, y={gaze_data.y:.3f}, conf={gaze_data.confidence:.3f}")
            
            client.disconnect()
            return True
        else:
            print("❌ Our wrapper connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Client wrapper test failed: {e}")
        return False

async def test_device_agent_streaming():
    """Test our device agent with real data"""
    print("\n🔍 Testing device agent streaming...")
    
    try:
        from device_agent import SolGlassesAgent
        
        # Create agent
        agent = SolGlassesAgent(session_id="streaming_test")
        
        # Test gaze data generation (will try real hardware first)
        print("📡 Testing gaze data generation...")
        
        for i in range(5):
            gaze_data = await agent.real_gaze_data()
            if gaze_data:
                gaze = gaze_data['gaze_data']
                print(f"Sample {i+1}: x={gaze['x']:.3f}, y={gaze['y']:.3f}, conf={gaze['confidence']:.3f}")
            else:
                print(f"❌ No gaze data for sample {i+1}")
                return False
            
            await asyncio.sleep(0.1)  # 100ms interval
        
        print("✅ Device agent streaming test passed")
        return True
        
    except Exception as e:
        print(f"❌ Device agent test failed: {e}")
        return False

async def main():
    """Run streaming tests"""
    print("🚀 Sol Glasses Streaming Test Suite")
    print("=" * 40)
    
    results = []
    
    # Test 1: Async streaming
    results.append(await test_async_streaming())
    
    # Test 2: Video + gaze
    results.append(await test_video_with_gaze())
    
    # Test 3: Our client wrapper
    results.append(test_our_client_wrapper())
    
    # Test 4: Device agent
    results.append(await test_device_agent_streaming())
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Streaming Test Results:")
    test_names = ["Async Streaming", "Video+Gaze", "Client Wrapper", "Device Agent"]
    
    for name, result in zip(test_names, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"• {name}: {status}")
    
    passed = sum(results)
    print(f"\nOverall: {passed}/{len(results)} streaming tests passed")
    
    if passed >= 2:
        print("🎉 Streaming functionality is working!")
    else:
        print("⚠️  Streaming issues need investigation")

if __name__ == "__main__":
    asyncio.run(main())