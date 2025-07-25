# Sol Glasses Backend Integration Test

Minimal backend for testing Sol Glasses hardware integration with WebSocket streaming.

## Quick Start

### 1. Setup Backend

```bash
cd backend_test/
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Backend Server

```bash
python main.py
```

Server will start at: http://localhost:8000

- WebSocket endpoint: `ws://localhost:8000/ws/sessions/{session_id}`
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/

### 3. Test Connection (Simulated Data)

```bash
# Test basic connection
python device_agent.py --test-only

# Stream simulated data for 30 seconds at 120 Hz
python device_agent.py --duration 30 --hz 120

# Custom session ID
python device_agent.py --session my_test_session
```

## Sol Glasses Hardware Setup

### Prerequisites

1. **Sol Glasses powered on** and connected to WiFi
2. **Sol SDK installed** on your development machine
3. **Network connectivity** between glasses and backend server

### Hardware Configuration Steps

#### Step 1: Install Sol SDK

```bash
# Install Sol SDK (check documentation for latest version)
pip install sol-sdk  # Replace with actual package name

# Or if you have a wheel file:
pip install path/to/sol_sdk-1.1.1-py3-none-any.whl
```

#### Step 2: Find Sol Glasses IP Address

**Option A: Check glasses display/settings**

- Look in Sol Glasses settings menu for WiFi/Network info

**Option B: Network scan**

```bash
# Scan local network for Ganzin devices
nmap -sn 192.168.1.0/24 | grep -i ganzin

# Or use ARP table
arp -a | grep -i ganzin
```

**Option C: Router admin panel**

- Check your WiFi router's connected devices list

#### Step 3: Test Sol SDK Connection

```bash
# Create test script to verify Sol SDK works
cat > test_sol_sdk.py << 'EOF'
import sys
try:
    from sol_sdk.synchronous import SyncClient
    from sol_sdk.synchronous.models import StreamingMode

    # Replace with your glasses IP address
    GLASSES_IP = "192.168.1.100"  # CHANGE THIS

    print(f"Testing connection to Sol Glasses at {GLASSES_IP}...")

    client = SyncClient(host=GLASSES_IP)

    # Test basic connection
    info = client.get_device_info()  # Replace with actual method
    print(f"Connected! Device info: {info}")

    # Test single capture
    result = client.capture()  # Replace with actual method
    print(f"Capture test successful: {result.timestamp}")

    print("✅ Sol SDK connection working!")

except ImportError as e:
    print(f"❌ Sol SDK not installed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("Check:")
    print("1. Glasses are powered on")
    print("2. Glasses are on same WiFi network")
    print("3. IP address is correct")
    print("4. No firewall blocking connection")
    sys.exit(1)
EOF

python test_sol_sdk.py
```

#### Step 4: Modify Device Agent for Real Hardware

Edit `device_agent.py` to use real Sol SDK:

```python
async def real_gaze_data(self):
    """Get real gaze data from Sol SDK"""
    try:
        from sol_sdk.synchronous import SyncClient

        # Initialize client with your glasses IP
        client = SyncClient(host="192.168.1.100")  # Your glasses IP

        # Capture gaze data
        result = client.capture()

        return {
            "timestamp": result.timestamp,
            "gaze_data": {
                "x": result.gaze_data.x,      # Adjust based on actual SDK
                "y": result.gaze_data.y,      # Adjust based on actual SDK
                "confidence": result.gaze_data.confidence
            },
            "scene_data": result.scene_image if hasattr(result, 'scene_image') else None
        }

    except Exception as e:
        logger.error(f"Sol SDK error: {e}")
        # Fallback to simulation for testing
        return await self.simulate_gaze_data()
```

#### Step 5: Run Full Integration Test

```bash
# Start backend server in one terminal
python main.py

# In another terminal, run device agent with real hardware
python device_agent.py --duration 60 --hz 120
```

### Network Configuration

#### Firewall Settings

Make sure port 8000 is open:

```bash
# Linux
sudo ufw allow 8000

# macOS
# Add rule in System Preferences > Security & Privacy > Firewall

# Windows
# Add inbound rule in Windows Firewall
```

#### If Backend is on Different Machine

Update URLs in device_agent.py:

```bash
# If backend runs on different machine
python device_agent.py --backend ws://192.168.1.50:8000
```

## API Endpoints

### WebSocket Endpoints

- `ws://localhost:8000/ws/sessions/{session_id}` - Gaze data streaming
- `ws://localhost:8000/ws/time-sync` - Time synchronization

### REST Endpoints

- `GET /` - Health check
- `GET /sessions` - List active sessions
- `GET /sessions/{session_id}/samples` - Get session samples
- `POST /sessions/{session_id}/calibrate` - Trigger calibration

## Expected Data Format

The WebSocket expects JSON messages in this format:

```json
{
  "timestamp": 1642781234567,
  "gaze_data": {
    "x": 0.5,
    "y": 0.3,
    "confidence": 0.95
  },
  "scene_data": "base64_encoded_image_optional"
}
```

## Testing Checklist

- [ ] Backend server starts without errors
- [ ] WebSocket connection accepts connections
- [ ] Simulated data streams at target frequency
- [ ] Real glasses hardware connects via Sol SDK
- [ ] Gaze data appears in backend logs
- [ ] Performance meets ≥120 Hz requirement
- [ ] Time synchronization works
- [ ] Frontend can connect and display data

## Troubleshooting

### Common Issues

**Backend won't start:**

```bash
# Check if port 8000 is in use
netstat -an | grep :8000
# Kill process using the port if needed
```

**WebSocket connection refused:**

- Check backend is running
- Verify no firewall blocking
- Try different port: `uvicorn main:app --port 8001`

**Sol SDK import errors:**

- Verify Sol SDK is properly installed
- Check Python virtual environment
- Review Sol SDK documentation for correct import paths

**Low performance/dropped samples:**

- Reduce target frequency: `--hz 60`
- Check network latency
- Monitor CPU/memory usage
- Use wired network connection

**Glasses not found:**

- Verify glasses are powered on
- Check WiFi connection
- Ping glasses IP address
- Review Sol SDK connection parameters

## Next Steps

After successful integration testing:

1. **Add PostgreSQL database** for persistent storage
2. **Implement authentication** and session management
3. **Add real-time processing** for AOI mapping
4. **Connect to frontend** for live gaze visualization
5. **Add calibration endpoints** and procedures
6. **Implement error handling** and reconnection logic

## Performance Targets

- **Streaming frequency**: ≥120 Hz
- **Latency**: <50ms end-to-end
- **Reliability**: 99.9% sample delivery
- **Session duration**: Support >30 minute sessions
