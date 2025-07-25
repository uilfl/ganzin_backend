# 🚀 Basic Sol SDK Test

🔍 Testing Sol SDK import...
✅ Sol SDK imported successfully

🔍 Testing hardware connection...
Connecting to Sol Glasses at 192.168.1.117:8080
Warning: Your SDK version is outdated in terms of minor versions, please update to 1.2.0.
✅ Connected! SDK Version: 1.2.0
✅ Device Status: Galaxy S24

🔍 Testing gaze data capture...
❌ Gaze capture failed: Expecting value: line 1 column 1 (char 0)

🔍 Testing recording functionality...
❌ Recording test failed: Expecting value: line 1 column 1 (char 0)

✅ Basic SDK test completed!
💡 If all tests passed, your Sol Glasses are ready for integration
(backend_test) chenyusheng@Working-Smart-4  ~/Developer/sol_glasses/backend_test   master ±  python3 test_so
l_connection.py
🚀 Sol Glasses Integration Test Suite
==================================================
🔍 Test 1: Testing Sol SDK import...
✅ Sol SDK import successful

🔍 Test 2: Testing Sol client wrapper...
INFO:config:Configuration loaded for environment: development
INFO:config:Configuration validation passed
✅ Mock client created successfully
INFO:sol_sdk_client:Mock: Connected to Sol Glasses
✅ Mock client connection successful
✅ Mock gaze data: x=0.292, y=0.726, confidence=0.811
✅ Mock device info: {'device_name': 'Mock Sol Glasses', 'sdk_version': '1.1.1', 'status': 'Connected'}
INFO:sol_sdk_client:Mock: Disconnected from Sol Glasses

🔍 Test 3: Testing real hardware connection...
Attempting connection to Sol Glasses at 192.168.1.117:8080
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.117:8080
Warning: Your SDK version is outdated in terms of minor versions, please update to 1.2.0.
INFO:sol_sdk_client:Connected to Sol Glasses SDK version: 1.2.0
INFO:sol_sdk_client:Device status: Galaxy S24
✅ Real hardware connection successful!
✅ Device info: {'device_name': 'Galaxy S24', 'sdk_version': '1.2.0', 'status': 'SUCCESS'}
ERROR:sol_sdk_client:Failed to capture gaze data: Expecting value: line 1 column 1 (char 0)
⚠️ No gaze data received
INFO:sol_sdk_client:Disconnected from Sol Glasses

🔍 Test 4: Testing streaming pattern from examples...
Testing streaming connection to 192.168.1.117:8080
Warning: Your SDK version is outdated in terms of minor versions, please update to 1.2.0.
✅ SDK Version: 1.2.0
✅ Device Status: Connected
❌ SDK direct connection failed: Expecting value: line 1 column 1 (char 0)

🔍 Test 5: Testing device agent streaming...
✅ Device agent created
ERROR:device_agent:Connection test failed: Multiple exceptions: [Errno 61] Connect call failed ('::1', 8000, 0, 0), [Errno 61] Connect call failed ('127.0.0.1', 8000)
⚠️ Device agent connection test failed (backend may not be running)
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x109a49810>, 'Connection to 192.168.1.100 timed out. (connect timeout=2.0)')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x109a69ba0>, 'Connection to 192.168.1.100 timed out. (connect timeout=2.0)')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x109a69cd0>, 'Connection to 192.168.1.100 timed out. (connect timeout=2.0)')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x109a1a330>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
✅ Gaze data generated: {
"timestamp": 1753377351337,
"gaze_data": {
"x": 0.5419392387595922,
"y": 0.4419005431752582,
"confidence": 0.8281688163469434
}
}

==================================================
📊 Test Results Summary:

1. SDK Import: ✅ PASS
2. Client Wrapper: ✅ PASS
3. Real Hardware: ✅ PASS
4. Example Streaming: ❌ FAIL
5. Device Agent: ✅ PASS

Overall: 4/5 tests passed
🎉 Sol Glasses integration is ready for testing!
(backend_test) chenyusheng@Working-Smart-4  ~/Developer/sol_glasses/backend_test   master ±  python3 test_st
reaming.py
🚀 Sol Glasses Streaming Test Suite
========================================
🔍 Testing async gaze streaming...
Connecting to Sol Glasses at 192.168.1.117:8080
Warning: Your SDK version is outdated in terms of minor versions, please update to 1.2.0.
✅ Async client connected
📡 Starting gaze stream (5 seconds)...
Sample 30: x=822.402, y=595.919 (80.1 Hz)
Sample 60: x=822.402, y=595.919 (83.3 Hz)
Sample 90: x=822.402, y=595.919 (87.1 Hz)
Sample 120: x=822.402, y=595.919 (88.2 Hz)
Sample 150: x=822.402, y=595.919 (90.8 Hz)
Sample 180: x=822.402, y=595.919 (92.6 Hz)
Sample 210: x=822.402, y=595.919 (95.2 Hz)
Sample 240: x=822.402, y=595.919 (96.7 Hz)
Sample 270: x=822.402, y=595.919 (96.8 Hz)
Sample 300: x=822.402, y=595.919 (97.4 Hz)
Sample 330: x=822.402, y=595.919 (97.4 Hz)
Sample 360: x=822.402, y=595.919 (97.5 Hz)
Sample 390: x=822.402, y=595.919 (97.4 Hz)
Sample 420: x=822.402, y=595.919 (98.7 Hz)
Sample 450: x=822.402, y=595.919 (98.3 Hz)
Sample 480: x=822.402, y=595.919 (98.0 Hz)
✅ Streaming test completed: 489 samples in 5.0s (97.8 Hz)

🔍 Testing video + gaze streaming...
Warning: Your SDK version is outdated in terms of minor versions, please update to 1.2.0.
✅ Video+gaze client connected
❌ Video+gaze test failed: mpeg4-generic/24000

🔍 Testing our client wrapper...
INFO:config:Configuration loaded for environment: development
INFO:config:Configuration validation passed
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.117:8080
Warning: Your SDK version is outdated in terms of minor versions, please update to 1.2.0.
INFO:sol_sdk_client:Connected to Sol Glasses SDK version: 1.2.0
INFO:sol_sdk_client:Device status: Galaxy S24
✅ Our wrapper connected successfully
✅ Device info: {'device_name': 'Galaxy S24', 'sdk_version': '1.2.0', 'status': 'SUCCESS'}
ERROR:sol_sdk_client:Failed to capture gaze data: Expecting value: line 1 column 1 (char 0)
INFO:sol_sdk_client:Disconnected from Sol Glasses

🔍 Testing device agent streaming...
📡 Testing gaze data generation...
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x10edd8cd0>, 'Connection to 192.168.1.100 timed out. (connect timeout=2.0)')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x10edd82d0>, 'Connection to 192.168.1.100 timed out. (connect timeout=2.0)')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x10ed71ba0>, 'Connection to 192.168.1.100 timed out. (connect timeout=2.0)')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ed723f0>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
Sample 1: x=0.599, y=0.648, conf=0.825
INFO:aiortsp.rtsp.reader:connection closed, error:
INFO:aiortsp.rtsp.reader:connection to RTSP server 192.168.1.117:8086 closed (error: None)
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ee05eb0>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ed2b130>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ed2ae00>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ed2b350>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
Sample 2: x=0.141, y=0.535, conf=0.893
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ed2b680>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ed2b8a0>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ed2bac0>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ed2bce0>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
Sample 3: x=0.482, y=0.322, conf=0.804
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ee20050>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ee20270>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ee20490>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ee206b0>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
Sample 4: x=0.329, y=0.278, conf=0.849
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ee20c00>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ee20e20>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ee21040>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10ee21260>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
Sample 5: x=0.364, y=0.756, conf=0.940
✅ Device agent streaming test passed

========================================
📊 Streaming Test Results:
• Async Streaming: ✅ PASS
• Video+Gaze: ❌ FAIL
• Client Wrapper: ✅ PASS
• Device Agent: ✅ PASS

Overall: 3/4 streaming tests passed
🎉 Streaming functionality is working!
(backend_test) chenyusheng@Working-Smart-4  ~/Developer/sol_glasses/backend_test   master ±  python3 test_streaming.py
🚀 Sol Glasses Streaming Test Suite
========================================
🔍 Testing async gaze streaming...
Connecting to Sol Glasses at 192.168.1.117:8080
Warning: Your SDK version is outdated in terms of minor versions, please update to 1.2.0.
✅ Async client connected
📡 Starting gaze stream (5 seconds)...
Sample 30: x=639.632, y=580.465 (81.6 Hz)
Sample 60: x=617.667, y=659.301 (86.2 Hz)
Sample 90: x=628.801, y=682.290 (89.6 Hz)
Sample 120: x=660.987, y=689.111 (91.7 Hz)
Sample 150: x=784.189, y=478.868 (92.9 Hz)
Sample 180: x=623.077, y=754.480 (93.8 Hz)
Sample 210: x=659.413, y=345.688 (95.1 Hz)
Sample 240: x=584.669, y=319.383 (96.3 Hz)
Sample 270: x=723.317, y=327.541 (97.2 Hz)
Sample 300: x=720.682, y=330.230 (97.9 Hz)
Sample 330: x=1037.163, y=392.985 (98.6 Hz)
Sample 360: x=930.844, y=394.982 (98.3 Hz)
Sample 390: x=649.166, y=683.355 (97.6 Hz)
Sample 420: x=694.387, y=700.886 (98.6 Hz)
Sample 450: x=559.987, y=889.028 (98.0 Hz)
Sample 480: x=576.938, y=889.690 (98.4 Hz)
✅ Streaming test completed: 492 samples in 5.0s (98.1 Hz)

🔍 Testing video + gaze streaming...
Warning: Your SDK version is outdated in terms of minor versions, please update to 1.2.0.
✅ Video+gaze client connected
❌ Video+gaze test failed: mpeg4-generic/24000

🔍 Testing our client wrapper...
INFO:config:Configuration loaded for environment: development
INFO:config:Configuration validation passed
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.117:8080
Warning: Your SDK version is outdated in terms of minor versions, please update to 1.2.0.
INFO:sol_sdk_client:Connected to Sol Glasses SDK version: 1.2.0
INFO:sol_sdk_client:Device status: Galaxy S24
✅ Our wrapper connected successfully
✅ Device info: {'device_name': 'Galaxy S24', 'sdk_version': '1.2.0', 'status': 'SUCCESS'}
ERROR:sol_sdk_client:Failed to capture gaze data: Expecting value: line 1 column 1 (char 0)
INFO:sol_sdk_client:Disconnected from Sol Glasses

🔍 Testing device agent streaming...
📡 Testing gaze data generation...
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e0e5090>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e0e4690>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e012fd0>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e013820>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
Sample 1: x=0.603, y=0.550, conf=0.804
INFO:aiortsp.rtsp.reader:connection closed, error:
INFO:aiortsp.rtsp.reader:connection to RTSP server 192.168.1.117:8086 closed (error: None)
INFO:aiortsp.rtsp.reader:stopping stream...
INFO:aiortsp.rtsp.reader:stopping session/playback...
INFO:aiortsp.rtsp.reader:connection closed, error:
INFO:aiortsp.rtsp.reader:connection to RTSP server 192.168.1.117:8086 closed (error: None)
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e136450>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03e9c0>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03ee00>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03f130>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
Sample 2: x=0.118, y=0.467, conf=0.899
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03f460>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03f680>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03f8a0>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03fac0>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
Sample 3: x=0.478, y=0.678, conf=0.956
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03fdf0>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e144050>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e144270>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e144490>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
Sample 4: x=0.287, y=0.565, conf=0.963
INFO:sol_sdk_client:Connecting to Sol Glasses at 192.168.1.100:8080
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03f8a0>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03f680>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03f460>: Failed to establish a new connection: [Errno 64] Host is down')': /api/version
ERROR:sol_sdk_client:Failed to connect to Sol Glasses: HTTPConnectionPool(host='192.168.1.100', port=8080): Max retries exceeded with url: /api/version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10e03f350>: Failed to establish a new connection: [Errno 64] Host is down'))
WARNING:device_agent:Sol Glasses connection failed, using simulation
Sample 5: x=0.484, y=0.737, conf=0.948
✅ Device agent streaming test passed

========================================
📊 Streaming Test Results:
• Async Streaming: ✅ PASS
• Video+Gaze: ❌ FAIL
• Client Wrapper: ✅ PASS
• Device Agent: ✅ PASS

Overall: 3/4 streaming tests passed
🎉 Streaming functionality is working!
