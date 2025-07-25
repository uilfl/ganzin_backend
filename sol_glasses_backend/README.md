# Sol Glasses Backend

Complete backend system for Sol Glasses eye-tracking educational platform implementing all product requirements (R1-R13).

## Project Structure

```
sol_glasses_backend/
├── src/
│   ├── core/                 # Core business logic
│   │   ├── __init__.py
│   │   ├── database.py       # Database operations (R3)
│   │   ├── processing.py     # Gaze processing (R4) 
│   │   ├── adaptation.py     # Adaptive feedback (R5)
│   │   └── sol_client.py     # Sol SDK integration
│   ├── services/             # Service layer
│   │   ├── __init__.py
│   │   ├── ingestion.py      # R3: High-performance ingestion
│   │   ├── processing.py     # R4: Event detection
│   │   ├── adaptation.py     # R5: Real-time feedback
│   │   ├── reporting.py      # R6: PDF/JSON reports
│   │   └── nlp.py           # R7/R8: Language processing
│   ├── api/                  # API layer
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── websocket.py     # WebSocket handlers
│   │   ├── routes/          # REST API routes
│   │   └── middleware.py    # Custom middleware
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   ├── database.py      # Database models
│   │   ├── api.py          # API models
│   │   └── processing.py    # Processing models
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── config.py        # Configuration management
│       ├── logging.py       # Logging setup
│       └── exceptions.py    # Custom exceptions
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/               # End-to-end tests
├── docs/                   # Documentation
├── scripts/               # Deployment/utility scripts
├── config/               # Configuration files
└── requirements.txt      # Dependencies
```

## Features Implemented

### ✅ Core Requirements
- **R3**: High-performance ingestion with PostgreSQL COPY (≤50ms p95)
- **R4**: Real-time gaze processing with I-DT fixation detection (≥95% precision)
- **R5**: Adaptive feedback system with WebSocket commands (≤200ms latency)
- **R6**: PDF/JSON report generation (≤5MB, ≥24h validity)
- **R7**: Vocabulary assistance (>1.5s fixation triggers)
- **R8**: Grammar help for complex sentences
- **R9**: Personalized revision lists from fixation hotspots

### ✅ Technical Features
- **Sol SDK Integration**: Correct API usage with SyncClient
- **WebSocket Streaming**: Real-time bidirectional communication
- **Database Schema**: Complete PostgreSQL schema for all requirements
- **Configuration Management**: Environment-based configuration
- **Error Handling**: Comprehensive error handling and logging
- **Testing Framework**: Unit, integration, and E2E test structure

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Sol Glasses hardware (or mock mode for development)

### Installation
```bash
cd sol_glasses_backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
```bash
# Copy environment template
cp config/.env.example .env

# Edit configuration
export DATABASE_URL="postgresql://user:pass@localhost:5432/sol_glasses"
export SOL_GLASSES_IP="192.168.1.100"
export USE_DATABASE=true
export DEBUG_MODE=false
```

### Database Setup
```bash
# Initialize database
python scripts/init_db.py

# Run migrations
python scripts/migrate.py
```

### Running the Server
```bash
# Development mode
python src/api/main.py

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### WebSocket
- `ws://localhost:8000/ws/sessions/{session_id}` - Gaze data streaming
- `ws://localhost:8000/ws/time-sync` - Time synchronization

### REST API
- `GET /` - Health check
- `GET /sessions` - List active sessions
- `GET /sessions/{session_id}/samples` - Get session samples
- `GET /sessions/{session_id}/revision` - Get revision list (R9)
- `GET /lessons/{lesson_id}/aois` - Get AOI definitions (R2)

## Performance Targets

- **Gaze Sampling**: ≥120 Hz with confidence ≥0.8
- **Ingestion Latency**: ≤50ms (p95) for bulk inserts
- **End-to-end Feedback**: ≤200ms from gaze event to UI response
- **Event Detection**: ≥95% precision on benchmark datasets
- **Report Generation**: ≤5MB files, valid for ≥24h

## Development

### Testing
```bash
# Run all tests
pytest tests/

# Unit tests only
pytest tests/unit/

# With coverage
pytest --cov=src tests/
```

### Code Quality
```bash
# Linting
flake8 src/
black src/
isort src/

# Type checking
mypy src/
```

### Database Migrations
```bash
# Create migration
python scripts/create_migration.py "migration_name"

# Apply migrations
python scripts/migrate.py
```

## Monitoring

### Health Checks
- Database connectivity
- Sol Glasses hardware status
- WebSocket connection status
- Processing pipeline health

### Metrics
- Gaze sample throughput (samples/second)
- Processing latency (event detection time)
- Feedback response time
- Error rates and types

## Troubleshooting

### Common Issues

**Sol Glasses Connection Failed**
```bash
# Check network connectivity
ping <glasses_ip>

# Verify Sol SDK installation
python -c "from sol_sdk.synchronous import SyncClient; print('SDK OK')"

# Check configuration
python -c "from src.utils.config import config; print(config.sol_sdk)"
```

**Database Connection Issues**
```bash
# Test database connectivity
psql $DATABASE_URL -c "SELECT version();"

# Check pool status
python scripts/check_db.py
```

**Performance Issues**
```bash
# Monitor WebSocket connections
python scripts/monitor_websockets.py

# Check processing pipeline
python scripts/debug_processing.py
```

## Deployment

### Docker
```bash
# Build image
docker build -t sol-glasses-backend .

# Run container
docker run -p 8000:8000 -e DATABASE_URL=... sol-glasses-backend
```

### Production Considerations
- Use PostgreSQL connection pooling
- Enable database TDE for R12 compliance
- Set up monitoring and alerting
- Configure log aggregation
- Use reverse proxy (nginx/traefik)
- Enable SSL/TLS termination

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create GitHub issue for bugs/features
- Check documentation in `docs/`
- Review configuration in `config/`