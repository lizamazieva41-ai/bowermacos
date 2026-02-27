# Bower Antidetect Browser V2

A professional Python-based browser automation system for managing anonymous browser profiles with advanced stealth capabilities. Designed for privacy-conscious automation tasks.

## Features

### Core Features
- **Headless Browser**: Run browsers in headless mode (50-70% RAM savings)
- **Profile Management**: Create, clone, import/export browser profiles
- **Multi-session**: Manage up to 50 concurrent browser sessions
- **CLI & API**: Control via Typer CLI or FastAPI server

### Stealth/Fingerprint Protection
- Custom User-Agent spoofing
- WebGL fingerprint randomization
- Canvas fingerprint protection
- WebRTC IP leak protection
- DNS leak protection
- Audio fingerprint masking
- Font fingerprint protection
- Timezone & language spoofing
- Navigator.webdriver hiding
- Chrome runtime detection removal
- Screen properties spoofing
- Hardware concurrency spoofing
- Device memory spoofing

### Additional Features
- Selenium integration (optional)
- Undetected Chromedriver integration (optional)
- Session recovery after crash
- Profile import/export (JSON format)
- Automatic browser updates

### Proxy Management
- HTTP/HTTPS/SOCKS5 proxy support
- Proxy authentication
- Proxy health monitoring
- Automatic proxy validation

### Security
- JWT authentication
- API key support
- Rate limiting
- Account lockout after failed attempts
- Audit logging
- TLS/SSL support

## Quick Start

### Installation

```bash
# Clone and setup
git clone https://github.com/your-repo/bower-macos.git
cd bower-macos

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Running the Server

```bash
# Start API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the run script
chmod +x ./run_local.sh
./run_local.sh
```

### Default Credentials
- Username: `admin`
- Password: `admin`

## CLI Usage

```bash
# Open a browser session
python3 -m src.cli.commands open --name my_profile

# Create a profile
python3 -m src.cli.commands create-profile --name my_profile --headless

# List profiles
python3 -m src.cli.commands list-profiles

# List active sessions
python3 -m src.cli.commands list-sessions

# Navigate to URL
python3 -m src.cli.commands navigate <session_id> https://example.com

# Take screenshot
python3 -m src.cli.commands screenshot <session_id> --path screenshot.png

# Click element
python3 -m src.cli.commands click <session_id> "#button-id"

# Type text
python3 -m src.cli.commands type-text <session_id> "#input-id" "Hello World"

# Execute JavaScript
python3 -m src.cli.commands execute <session_id> "return document.title;"

# Close session
python3 -m src.cli.commands close <session_id>

# Clone a profile
python3 -m src.cli.commands clone-profile 1 --name new_profile

# Export profile to JSON
python3 -m src.cli.commands export-profile 1 --output profile.json

# Import profile from JSON
python3 -m src.cli.commands import-profile profile.json

# Delete a profile
python3 -m src.cli.commands delete-profile 1

# Validate proxy
python3 -m src.cli.commands validate-proxy --proxy http://proxy:port

# Get session details
python3 -m src.cli.commands get-session <session_id>

# Check API health
python3 -m src.cli.commands health
```

## API Usage

### Authentication

```bash
# Login to get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Response:
# {"success":true,"data":{"access_token":"eyJ...","token_type":"bearer","expires_in":3600}}

# Or use API key
curl -X GET http://localhost:8000/api/v1/auth/api-key?name=mykey
```

### Profile Management

```bash
# List profiles
curl -X GET http://localhost:8000/api/v1/profiles \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create profile
curl -X POST http://localhost:8000/api/v1/profiles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "test-profile", "headless": true}'

# Clone profile
curl -X POST http://localhost:8000/api/v1/profiles/1/clone \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "cloned-profile"}'

# Export profile
curl -X GET http://localhost:8000/api/v1/profiles/1/export \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Session Management

```bash
# Create session from profile
curl -X POST "http://localhost:8000/api/v1/sessions?profile_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Navigate
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/navigate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Click element
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/click \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"selector": "#button-id"}'

# Type text
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/type \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"selector": "#input-id", "text": "Hello World"}'

# Screenshot
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/screenshot \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path": "screenshot.png"}'

# Execute JavaScript
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"script": "return document.title;"}'
```

### Proxy Management

```bash
# List proxies
curl -X GET http://localhost:8000/api/v1/proxies \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create proxy
curl -X POST http://localhost:8000/api/v1/proxies \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-proxy", "proxy_type": "http", "host": "proxy.example.com", "port": 8080}'

# Test proxy
curl -X POST http://localhost:8000/api/v1/proxies/1/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/login | Login with username/password |
| GET | /api/v1/auth/api-key | Generate API key |

### Profiles
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/profiles | List all profiles |
| POST | /api/v1/profiles | Create profile |
| GET | /api/v1/profiles/{id} | Get profile details |
| PUT | /api/v1/profiles/{id} | Update profile |
| DELETE | /api/v1/profiles/{id} | Delete profile |
| POST | /api/v1/profiles/{id}/clone | Clone profile |
| GET | /api/v1/profiles/{id}/export | Export profile |
| POST | /api/v1/profiles/import | Import profile |

### Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/sessions | List active sessions |
| POST | /api/v1/sessions | Create session |
| GET | /api/v1/sessions/{id} | Get session info |
| DELETE | /api/v1/sessions/{id} | Close session |
| POST | /api/v1/sessions/{id}/navigate | Navigate to URL |
| POST | /api/v1/sessions/{id}/click | Click element |
| POST | /api/v1/sessions/{id}/type | Type text |
| POST | /api/v1/sessions/{id}/screenshot | Take screenshot |
| POST | /api/v1/sessions/{id}/execute | Execute JavaScript |
| GET | /api/v1/sessions/{id}/page-source | Get page HTML |

### Proxies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/proxies | List proxies |
| POST | /api/v1/proxies | Create proxy |
| GET | /api/v1/proxies/{id} | Get proxy details |
| PUT | /api/v1/proxies/{id} | Update proxy |
| DELETE | /api/v1/proxies/{id} | Delete proxy |
| POST | /api/v1/proxies/{id}/test | Test proxy |
| GET | /api/v1/proxies/health | Health summary |

### Monitoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/metrics | Performance metrics |
| GET | /api/v1/recovery/status | Recovery status |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| /ws/session/{session_id} | Real-time browser control |

## Real-time Features

### WebSocket Client (GUI)
```python
from src.gui.utils.websocket_client import rt_manager

# Connect to session for real-time updates
client = rt_manager.connect_session("session_id")

# Register callback
def on_update(data):
    print(f"Session update: {data}")

rt_manager.register_session_callback("session_id", on_update)

# Disconnect when done
rt_manager.disconnect_session("session_id")
```

### Notifications System
```python
from src.gui.utils.notifications import show_success, show_error

show_success("Operation completed!")
show_error("Something went wrong")
show_warning("Warning message")
show_info("Information")
```

## Testing
- Dashboard with session statistics
- Profile management (create, edit, delete, clone)
- Session management (start, stop, monitor)
- Proxy management (add, edit, delete, test)
- Settings configuration with auto-refresh
- Real-time updates via WebSocket
- Toast notifications system

### GUI Pages
- **Login** - Authentication page
- **Dashboard** - Overview with stats cards
- **Profiles** - Create/edit/delete profiles
- **Sessions** - Monitor active sessions
- **Proxies** - Manage proxy servers
- **Settings** - App configuration

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_browser.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests
pytest tests/integration/ -v
```

## Architecture

```
src/
├── browser/           # Browser manager with Playwright
│   ├── manager.py     # Core browser session management
│   ├── stealth.py     # Anti-detection scripts
│   ├── fingerprint.py # Fingerprint generation
│   ├── timezone_sync.py
│   ├── font_protection.py
│   ├── recovery.py   # Session recovery
│   ├── selenium_integration.py
│   └── uc_integration.py
├── proxy/            # Proxy configuration
│   ├── loader.py
│   ├── validator.py
│   ├── health_monitor.py
│   ├── dns_leak.py
│   └── rotation.py
├── api/              # FastAPI endpoints
│   ├── routes.py
│   ├── auth.py
│   ├── schemas.py
│   ├── errors.py
│   ├── middleware.py
│   └── client.py
├── cli/              # Typer CLI commands
├── db/               # SQLite database (SQLAlchemy)
├── gui/              # DearPyGui desktop app
│   ├── app.py        # Main app class
│   ├── main.py       # Entry point
│   ├── pages/        # Dashboard, Profiles, Sessions, etc.
│   ├── components/   # Reusable UI components
│   ├── styles/       # Theme and styling
│   └── utils/        # API client, WebSocket, notifications
├── monitoring/       # Performance monitoring
│   └── metrics.py
└── utils/            # Utilities
    ├── profile_io.py
    ├── credentials.py
    └── ssl_config.py

tests/
├── unit/          # Unit tests
├── integration/   # Integration tests
├── e2e/          # End-to-end tests
└── stress/       # Performance tests

docs/
└── user-guide.md # Detailed user documentation
```
src/
├── browser/         # Browser manager with Playwright
│   ├── manager.py   # Core browser session management
│   ├── stealth.py   # Anti-detection scripts
│   ├── fingerprint.py
│   ├── timezone_sync.py
│   ├── font_protection.py
│   └── recovery.py  # Session recovery
├── proxy/          # Proxy configuration
│   ├── loader.py
│   ├── validator.py
│   ├── health_monitor.py
│   ├── dns_leak.py
│   └── rotation.py
├── api/            # FastAPI endpoints
│   ├── routes.py
│   ├── auth.py
│   ├── schemas.py
│   ├── errors.py
│   └── middleware.py
├── cli/            # Typer CLI commands
├── db/             # SQLite database (SQLAlchemy)
├── gui/            # DearPyGui desktop app
│   ├── pages/      # Dashboard, Profiles, Sessions, etc.
│   └── styles/    # Theme and styling
└── monitoring/     # Performance monitoring

tests/
├── unit/          # Unit tests
├── integration/   # Integration tests
├── e2e/          # End-to-end tests
└── stress/       # Performance tests
```

## Requirements

- Python 3.10+
- Playwright 1.40+
- Chromium browser
- FastAPI
- SQLAlchemy
- DearPyGui (for GUI)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection | sqlite+aiosqlite:///./bower.db |
| SECRET_KEY | JWT secret key | Generated |
| API_PORT | Server port | 8000 |
| HOST | Server host | 0.0.0.0 |
| LOG_LEVEL | Logging level | INFO |
| MAX_SESSIONS | Max concurrent sessions | 50 |
| DATA_DIR | Data storage directory | ./data |
| LOGS_DIR | Logs directory | ./logs |

## Security Considerations

- Always change default credentials in production
- Use strong API keys
- Enable TLS/SSL in production
- Implement proper rate limiting
- Regularly update dependencies

## License

MIT License

## Documentation

- [User Guide](./docs/user-guide.md) - Detailed usage instructions
- [API Documentation](#api-endpoints) - Complete API reference
- [Feature List](./Antidetect_Browser_Documentation/03_Functional_Specifications/01_Feature_List.md) - Feature specifications
- [Test Plan](./Antidetect_Browser_Documentation/11_Testing_Strategy/01_Test_Plan.md) - Testing strategy

## Support

For issues and feature requests, please open an issue on GitHub.
