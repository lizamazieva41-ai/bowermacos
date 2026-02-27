# Bower Antidetect Browser - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Profile Management](#profile-management)
5. [Session Management](#session-management)
6. [Proxy Configuration](#proxy-configuration)
7. [CLI Commands](#cli-commands)
8. [API Reference](#api-reference)
9. [GUI Application](#gui-application)
10. [Stealth Features](#stealth-features)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

Bower Antidetect Browser V2 is a professional privacy browser automation system that allows you to create and manage multiple browser profiles with advanced anti-detection capabilities.

### Key Features
- Headless browser mode (50-70% RAM savings)
- Advanced fingerprint spoofing
- Proxy rotation and management
- CLI and API control
- Desktop GUI application

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Chromium browser (installed via Playwright)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/your-repo/bower-macos.git
cd bower-macos
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers**
```bash
playwright install chromium
```

5. **Start the server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Quick Start

### Starting the API Server

```bash
# Default start
uvicorn main:app --host 0.0.0.0 --port 8000

# With auto-reload for development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with custom settings
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Default Credentials
- Username: `admin`
- Password: `admin`

**Important:** Change these credentials in production!

---

## Profile Management

### Creating a Profile

#### Via CLI
```bash
python3 -m src.cli.commands create-profile --name my_profile
```

#### Via API
```bash
curl -X POST http://localhost:8000/api/v1/profiles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_profile",
    "browser_engine": "chromium",
    "user_agent": "Mozilla/5.0...",
    "proxy": "http://proxy:port",
    "resolution": "1920x1080",
    "timezone": "America/New_York",
    "language": "en-US",
    "headless": true
  }'
```

### Profile Options

| Option | Description | Default |
|--------|-------------|---------|
| name | Profile name (required) | - |
| browser_engine | chromium, firefox, webkit | chromium |
| user_agent | Custom User-Agent string | Auto-generated |
| proxy | Proxy URL (http/socks5) | None |
| resolution | Screen resolution | 1920x1080 |
| timezone | Timezone (e.g., America/New_York) | System |
| language | Browser language (e.g., en-US) | en-US |
| headless | Run in headless mode | true |

### Cloning a Profile

```bash
# Via CLI
python3 -m src.cli.commands clone-profile 1 --name cloned_profile

# Via API
curl -X POST http://localhost:8000/api/v1/profiles/1/clone \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "cloned_profile"}'
```

### Import/Export Profiles

```bash
# Export
python3 -m src.cli.commands export-profile 1 --output profile.json

# Import
python3 -m src.cli.commands import-profile profile.json
```

---

## Session Management

### Starting a Session

```bash
# Via CLI
python3 -m src.cli.commands open --name my_profile

# Via API
curl -X POST "http://localhost:8000/api/v1/sessions?profile_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Session Operations

```bash
# Navigate to URL
python3 -m src.cli.commands navigate <session_id> https://example.com

# Click element
python3 -m src.cli.commands click <session_id> "#button-id"

# Type text
python3 -m src.cli.commands type-text <session_id> "#input-id" "Hello World"

# Take screenshot
python3 -m src.cli.commands screenshot <session_id> --path screenshot.png

# Execute JavaScript
python3 -m src.cli.commands execute <session_id> "return document.title;"

# Close session
python3 -m src.cli.commands close <session_id>
```

---

## Proxy Configuration

### Adding a Proxy

```bash
# Via CLI
# Not directly supported, use API

# Via API
curl -X POST http://localhost:8000/api/v1/proxies \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_proxy",
    "proxy_type": "http",
    "host": "proxy.example.com",
    "port": 8080,
    "username": "user",
    "password": "pass",
    "is_active": true
  }'
```

### Proxy Types
- `http` - HTTP proxy
- `https` - HTTPS proxy
- `socks5` - SOCKS5 proxy

### Testing a Proxy

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/proxies/1/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Proxy in Profile

```bash
# Create profile with proxy
curl -X POST http://localhost:8000/api/v1/profiles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "profile_with_proxy",
    "proxy": "http://user:pass@proxy.example.com:8080"
  }'
```

---

## CLI Commands

### Available Commands

| Command | Description |
|---------|-------------|
| `open` | Open a new browser session |
| `navigate` | Navigate to URL |
| `click` | Click an element |
| `type-text` | Type text into element |
| `screenshot` | Take screenshot |
| `execute` | Execute JavaScript |
| `list-sessions` | List active sessions |
| `list-profiles` | List all profiles |
| `create-profile` | Create new profile |
| `delete-profile` | Delete profile |
| `clone-profile` | Clone profile |
| `export-profile` | Export profile to JSON |
| `import-profile` | Import profile from JSON |
| `validate-proxy` | Validate proxy |
| `health` | Check API health |

### Examples

```bash
# Open session with custom options
python3 -m src.cli.commands open \
  --name my_session \
  --proxy http://proxy:8080 \
  --ua "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  --headless

# Create profile with all options
python3 -m src.cli.commands create-profile \
  --name my_profile \
  --proxy http://proxy:8080 \
  --resolution 1920x1080 \
  --timezone "America/New_York" \
  --language "en-US"
```

---

## API Reference

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Response
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}

# Get API Key
curl -X GET "http://localhost:8000/api/v1/auth/api-key?name=mykey&days_valid=365" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| /api/v1/auth/login | 5/minute |
| /api/v1/auth/api-key | 3/minute |
| /api/v1/profiles (GET) | 100/minute |
| /api/v1/profiles (POST) | 50/minute |
| /api/v1/proxies (GET) | 60/minute |
| /api/v1/proxies (POST) | 30/minute |
| /api/v1/sessions (GET) | 60/minute |
| /api/v1/sessions (POST) | 30/minute |

### Error Codes

| Code | Meaning |
|------|---------|
| 1001 | Validation Error |
| 2001 | Network Error |
| 3001 | Authentication Error |
| 4001 | System Error |
| 5001 | Session Error |
| 6001 | Proxy Error |
| 7001 | Profile Error |

---

## GUI Application

### Starting GUI

```bash
python3 -m src.gui.main
```

### GUI Features

1. **Dashboard** - Overview of sessions and system stats
2. **Profiles** - Create, edit, delete, clone profiles
3. **Sessions** - Manage active browser sessions
4. **Proxies** - Add and manage proxy servers
5. **Settings** - Configure application settings

### GUI Settings

- API Server URL
- Default browser engine
- Default resolution
- Headless mode default
- Auto-refresh interval

---

## Stealth Features

### Implemented Protections

1. **Navigator.webdriver** - Returns `false`
2. **WebGL** - Fake vendor/renderer
3. **Canvas** - Randomization
4. **WebRTC** - Blocked
5. **Audio** - Fingerprint masking
6. **Fonts** - Protection enabled
7. **Timezone** - Matches proxy location
8. **Language** - Configurable

### Testing Stealth

Run the E2E stealth tests:

```bash
pytest tests/e2e/test_anti_bot.py -v
```

---

## Troubleshooting

### Common Issues

#### "Browser not found"
```bash
# Install Playwright browsers
playwright install chromium
```

#### "Module not found"
```bash
# Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

#### "Connection refused"
```bash
# Make sure server is running
uvicorn main:app --host 0.0.0.0 --port 8000

# Check if port is available
lsof -i :8000
```

#### "Proxy not working"
```bash
# Test proxy separately
python3 -m src.cli.commands validate-proxy --proxy http://proxy:port
```

#### "Authentication failed"
```bash
# Check credentials
# Default: admin/admin

# Check token expiration
# Tokens expire after 60 minutes
```

### Logs

Check logs for detailed error information:

```bash
# Server logs
uvicorn main:app --log-level debug
```

### Performance

If experiencing performance issues:

1. Reduce concurrent sessions (default max: 50)
2. Use headless mode
3. Close unused sessions
4. Monitor memory usage via `/api/v1/metrics`

---

## Security Best Practices

1. **Change default credentials** - Update admin password immediately
2. **Use API keys** - Instead of username/password
3. **Enable TLS** - Use HTTPS in production
4. **Rate limiting** - Already enabled by default
5. **Audit logs** - Review regularly at `/api/v1/audit`

---

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review test cases for examples
