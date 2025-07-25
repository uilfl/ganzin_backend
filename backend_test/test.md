# Sol Glasses Integration Test Guide

This guide will help you test the Sol Glasses integration step by step and report any issues.

## Prerequisites

✅ **Already Done:**

- Sol SDK installed with `uv pip install ganzin_sol_sdk-1.1.1-py3-none-any.whl`
- Sol Glasses hardware connected and accessible

## Test Scripts Overview

| Script                   | Purpose                 | What It Tests                                       |
| ------------------------ | ----------------------- | --------------------------------------------------- |
| `test_basic_sdk.py`      | Basic connectivity      | SDK import, hardware connection, capture, recording |
| `test_streaming.py`      | Streaming functionality | Async streaming, video+gaze, our wrappers           |
| `test_sol_connection.py` | Comprehensive test      | All integration components                          |

## Step-by-Step Testing

### Step 1: Basic SDK Test

```bash
cd /Users/chenyusheng/Developer/sol_glasses/backend_test
python test_basic_sdk.py
```

**Expected Output:**

```
🚀 Basic Sol SDK Test
==============================
🔍 Testing Sol SDK import...
✅ Sol SDK imported successfully

🔍 Testing hardware connection...
Connecting to Sol Glasses at 192.168.2.19:8080
✅ Connected! SDK Version: X.X.X
✅ Device Status: Sol Glasses Device

🔍 Testing gaze data capture...
✅ Capture successful: <class 'sol_sdk.responses.CaptureResult'>
✅ Capture result received

🔍 Testing recording functionality...
✅ Recording started
✅ Tag added
✅ Recording stopped

✅ Basic SDK test completed!
```

**⚠️ Report These Issues:**

- ❌ Sol SDK import failed
- ❌ Hardware connection failed
- ❌ Gaze capture failed
- ❌ Recording test failed

### Step 2: Streaming Test

```bash
python test_streaming.py
```

**Expected Output:**

```
🚀 Sol Glasses Streaming Test Suite
========================================
🔍 Testing async gaze streaming...
Connecting to Sol Glasses at 192.168.2.19:8080
✅ Async client connected
📡 Starting gaze stream (5 seconds)...
Sample 30: x=0.456, y=0.623 (127.3 Hz)
Sample 60: x=0.489, y=0.601 (125.8 Hz)
✅ Streaming test completed: 642 samples in 5.0s (128.4 Hz)

🔍 Testing video + gaze streaming...
✅ Video+gaze client connected
✅ Received 10 video frames and 50 gaze samples

🔍 Testing our client wrapper...
✅ Our wrapper connected successfully
✅ Device info: {'device_name': 'Sol Glasses', 'sdk_version': '1.1.1', 'status': 'Connected'}
✅ Gaze data: x=0.542, y=0.387, conf=0.943

🔍 Testing device agent streaming...
📡 Testing gaze data generation...
Sample 1: x=0.432, y=0.567, conf=0.912
Sample 2: x=0.445, y=0.578, conf=0.898
Sample 3: x=0.439, y=0.572, conf=0.923
Sample 4: x=0.441, y=0.569, conf=0.907
Sample 5: x=0.448, y=0.573, conf=0.931
✅ Device agent streaming test passed

📊 Streaming Test Results:
• Async Streaming: ✅ PASS
• Video+Gaze: ✅ PASS
• Client Wrapper: ✅ PASS
• Device Agent: ✅ PASS

Overall: 4/4 streaming tests passed
🎉 Streaming functionality is working!
```

**⚠️ Report These Issues:**

- ❌ Async streaming test failed
- ❌ Video+gaze test failed
- ❌ Client wrapper test failed
- ❌ Device agent test failed
- Low Hz rates (< 100 Hz)
- No gaze data received

### Step 3: Comprehensive Test

```bash
python test_sol_connection.py
```

This runs all tests together and provides a complete integration report.

## Issue Reporting Template

When you find issues, please report them using this format:

### Issue Report

**Test Script:** `[script name]`
**Test Step:** `[which test failed]`
**Error Message:**

```
[paste exact error message here]
```

**Expected vs Actual:**

- Expected: [what should happen]
- Actual: [what actually happened]

**System Info:**

- Sol Glasses IP: 192.168.2.19
- Sol SDK Version: [from test output]
- Python Version: [your python version]

## Common Issues & Solutions

### 1. Connection Failed

**Symptoms:** `❌ Hardware connection failed`
**Solutions:**

- Check Sol Glasses are powered on
- Verify IP address (192.168.2.19:8080)
- Check network connectivity: `ping 192.168.2.19`
- Ensure no firewall blocking port 8080

### 2. SDK Import Failed

**Symptoms:** `❌ Sol SDK import failed`
**Solutions:**

- Verify wheel installation: `pip list | grep ganzin`
- Reinstall: `uv pip install --force-reinstall ganzin_sol_sdk-1.1.1-py3-none-any.whl`

### 3. Low Sampling Rate

**Symptoms:** Hz < 100 in streaming tests
**Solutions:**

- Check glasses battery level
- Verify USB/wireless connection quality
- Close other applications using glasses

### 4. No Gaze Data

**Symptoms:** `❌ No gaze data received`
**Solutions:**

- Check eye tracking calibration
- Ensure proper glasses positioning
- Verify lighting conditions

## Next Steps After Testing

Once all tests pass:

1. **Integration with Backend:** Test WebSocket server
2. **Frontend Integration:** Connect real gaze data to React components
3. **End-to-End Testing:** Full pipeline glasses → backend → frontend

## Test Results Log

Fill this out as you run tests:

- [ ] `test_basic_sdk.py`: ✅ PASS / ❌ FAIL
- [ ] `test_streaming.py`: ✅ PASS / ❌ FAIL
- [ ] `test_sol_connection.py`: ✅ PASS / ❌ FAIL

**Issues Found:**

1. [List any issues here]
2.
3.

**Ready for Next Phase:** YES / NO

---

💡 **Tip:** Run tests with glasses properly positioned on your head for best results. The eye tracking needs to see your eyes clearly for accurate gaze data.
