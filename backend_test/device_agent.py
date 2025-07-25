#!/usr/bin/env python3
"""
Sol Glasses Device Agent Test Script

This script simulates or connects to actual Sol Glasses hardware
and streams gaze data to the backend WebSocket server.

Fixed Sol SDK integration based on actual API documentation.
"""

import asyncio
import json
import logging
import time
import random
from typing import Optional
import websockets
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SolGlassesAgent:
    """Agent for streaming gaze data from Sol Glasses to backend"""
    
    def __init__(self, backend_url: str = "ws://localhost:8000", session_id: Optional[str] = None):
        self.backend_url = backend_url
        self.session_id = session_id or f"test_session_{int(time.time())}"
        self.websocket_url = f"{backend_url}/ws/sessions/{self.session_id}"
        self.time_sync_url = f"{backend_url}/ws/time-sync"
        self.running = False
        
    async def simulate_gaze_data(self):
        """
        Simulate realistic gaze data for testing
        In production, this would come from Sol SDK
        """
        # Simulate gaze movement in a reading pattern
        base_x = random.uniform(0.1, 0.9)  # Reading line position
        base_y = random.uniform(0.2, 0.8)  # Vertical reading position
        
        # Add small random movements (saccades/fixations)
        x = max(0.0, min(1.0, base_x + random.uniform(-0.05, 0.05)))
        y = max(0.0, min(1.0, base_y + random.uniform(-0.02, 0.02)))
        
        # Simulate confidence (higher when fixating)
        confidence = random.uniform(0.8, 0.98)
        
        return {
            "timestamp": int(time.time() * 1000),
            "gaze_data": {
                "x": x,
                "y": y,
                "confidence": confidence
            }
        }
    
    async def real_gaze_data(self):
        """
        Get real gaze data from Sol SDK
        Connect to Sol Glasses on port 8080 as per product requirements
        """
        USE_REAL_HARDWARE = True  # Try real hardware first, fallback to simulation
        
        if USE_REAL_HARDWARE:
            try:
                # Check if Sol SDK wheel is available
                import sys
                import os
                sdk_wheel_path = "/Users/chenyusheng/Developer/sol_glasses/backend_test/ganzin_sol_sdk-1.1.1-py3-none-any.whl"
                
                if os.path.exists(sdk_wheel_path):
                    # Import Sol SDK from wheel
                    from ganzin.sol_sdk.synchronous.sync_client import SyncClient
                    from ganzin.sol_sdk.synchronous.models import StreamingMode
                    
                    # Use the corrected Sol SDK client
                    from sol_sdk_client import create_sol_glasses_client
                    
                    # Create client using the wrapper
                    client = create_sol_glasses_client(
                        address=config.sol_sdk.default_address,
                        port=config.sol_sdk.default_port
                    )
                    
                    # Connect and capture data
                    if client.connect():
                        gaze_data = client.capture_gaze_data()
                        client.disconnect()
                        
                        if gaze_data:
                            return {
                                "timestamp": gaze_data.timestamp,
                                "gaze_data": {
                                    "x": gaze_data.x,
                                    "y": gaze_data.y,
                                    "confidence": gaze_data.confidence
                                },
                                "scene_data": gaze_data.scene_image
                            }
                    
                    # Fallback to simulation if connection failed
                    logger.warning("Sol Glasses connection failed, using simulation")
                    return await self.simulate_gaze_data()
                else:
                    logger.warning("Sol SDK wheel not found, using simulation")
                    return await self.simulate_gaze_data()
                
            except ImportError as e:
                logger.warning(f"Sol SDK import failed: {e}, using simulation")
                return await self.simulate_gaze_data()
            except Exception as e:
                logger.error(f"Sol hardware connection error: {e}, using simulation")
                return await self.simulate_gaze_data()
        else:
            return await self.simulate_gaze_data()
    
    async def sync_time(self):
        """Synchronize time with backend server (optional)"""
        try:
            async with websockets.connect(self.time_sync_url) as websocket:
                import struct
                
                # Send current time as 8-byte timestamp
                client_time = int(time.time() * 1000)
                request = struct.pack("!Q", client_time)
                
                await websocket.send(request)
                response = await websocket.recv()
                
                if len(response) == 16:
                    client_echo, server_time = struct.unpack("!QQ", response)
                    time_offset = server_time - client_time
                    logger.info(f"Time sync: offset={time_offset}ms")
                    return time_offset
                    
        except Exception as e:
            logger.warning(f"Time sync failed: {e}")
            return 0
    
    async def stream_gaze_data(self, duration_seconds: int = 60, target_hz: float = 120.0):
        """
        Stream gaze data to backend WebSocket
        
        Args:
            duration_seconds: How long to stream data
            target_hz: Target sampling frequency (Hz)
        """
        logger.info(f"Starting gaze data stream to {self.websocket_url}")
        logger.info(f"Target: {target_hz} Hz for {duration_seconds} seconds")
        
        # Optional: Sync time with server
        await self.sync_time()
        
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                logger.info(f"Connected to backend, session: {self.session_id}")
                
                self.running = True
                sample_count = 0
                start_time = time.time()
                target_interval = 1.0 / target_hz  # Time between samples
                
                while self.running and (time.time() - start_time) < duration_seconds:
                    loop_start = time.time()
                    
                    # Get gaze data (simulated or real)
                    gaze_sample = await self.real_gaze_data()
                    
                    # Send to backend
                    await websocket.send(json.dumps(gaze_sample))
                    
                    # Wait for optional confirmation
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                        response_data = json.loads(response)
                        if "error" in response_data:
                            logger.error(f"Backend error: {response_data['error']}")
                    except asyncio.TimeoutError:
                        pass  # No response, continue
                    except Exception as e:
                        logger.debug(f"Response parsing error: {e}")
                    
                    sample_count += 1
                    
                    # Log stats every 100 samples
                    if sample_count % 100 == 0:
                        elapsed = time.time() - start_time
                        actual_hz = sample_count / elapsed
                        logger.info(f"Samples: {sample_count}, Rate: {actual_hz:.1f} Hz")
                    
                    # Maintain target frequency
                    loop_time = time.time() - loop_start
                    sleep_time = max(0, target_interval - loop_time)
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)
                
                # Final stats
                total_time = time.time() - start_time
                final_hz = sample_count / total_time
                logger.info(f"Stream completed: {sample_count} samples in {total_time:.1f}s ({final_hz:.1f} Hz)")
                
        except websockets.exceptions.ConnectionClosed:
            logger.error("Connection to backend closed unexpectedly")
        except Exception as e:
            logger.error(f"Streaming error: {e}")
        finally:
            self.running = False
    
    async def test_connection(self):
        """Test connection to backend"""
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                # Send test message
                test_data = {
                    "timestamp": int(time.time() * 1000),
                    "gaze_data": {"x": 0.5, "y": 0.5, "confidence": 1.0},
                    "test": True
                }
                
                await websocket.send(json.dumps(test_data))
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                logger.info(f"Test successful: {response}")
                return True
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def stop(self):
        """Stop streaming"""
        self.running = False
        logger.info("Stopping gaze data stream...")


async def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sol Glasses Device Agent Test")
    parser.add_argument("--backend", default="ws://localhost:8000", help="Backend WebSocket URL")
    parser.add_argument("--session", default=None, help="Session ID")
    parser.add_argument("--duration", type=int, default=30, help="Streaming duration (seconds)")
    parser.add_argument("--hz", type=float, default=120.0, help="Target frequency (Hz)")
    parser.add_argument("--test-only", action="store_true", help="Only test connection")
    
    args = parser.parse_args()
    
    # Create agent
    agent = SolGlassesAgent(
        backend_url=args.backend,
        session_id=args.session
    )
    
    if args.test_only:
        logger.info("Testing connection only...")
        success = await agent.test_connection()
        if success:
            logger.info("✅ Connection test passed!")
        else:
            logger.error("❌ Connection test failed!")
        return
    
    try:
        # Start streaming
        await agent.stream_gaze_data(
            duration_seconds=args.duration,
            target_hz=args.hz
        )
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        agent.stop()


if __name__ == "__main__":
    asyncio.run(main())