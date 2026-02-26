# Stealth Browser - Antidetect Browser System V2

A Python-based browser automation system for managing anonymous browser profiles with stealth capabilities.

## Features

- **Headless Browser**: Run browsers in headless mode (50-70% RAM savings)
- **Fingerprint Spoofing**: Custom User-Agent, WebGL, Canvas, timezone, language
- **Proxy Support**: HTTP/SOCKS5 proxy with authentication
- **Stealth Mode**: Hide navigator.webdriver, plugins, and other detection vectors
- **Multi-session**: Manage up to 50 concurrent browser sessions
- **CLI & API**: Control via Typer CLI or FastAPI server

## Quick Start

### Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### CLI Usage

```bash
# Open a browser session
python -m src.cli.commands open --name my_profile

# Navigate to URL
python -m src.cli.commands navigate <session_id> https://example.com

# Take screenshot
python -m src.cli.commands screenshot <session_id> --path screenshot.png

# List active sessions
python -m src.cli.commands list-sessions

# Close session
python -m src.cli.commands close <session_id>
```

### API Usage

```bash
# Start API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Create session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "proxy": "http://host:port"}'

# Navigate
curl -X POST http://localhost:8000/sessions/{session_id}/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /sessions | Create new session |
| GET | /sessions | List all sessions |
| GET | /sessions/{id} | Get session info |
| DELETE | /sessions/{id} | Close session |
| POST | /sessions/{id}/navigate | Navigate to URL |
| POST | /sessions/{id}/click | Click element |
| POST | /sessions/{id}/type | Type text |
| POST | /sessions/{id}/screenshot | Take screenshot |
| POST | /sessions/{id}/execute | Execute JavaScript |

## Testing

```bash
pytest                          # Run all tests
pytest tests/integration/ -v   # Integration tests
pytest --cov=src --cov-report=html  # With coverage
```

## Architecture

```
src/
├── browser/     # Browser manager with Playwright
├── proxy/       # Proxy configuration and validation
├── api/         # FastAPI endpoints
├── cli/         # Typer CLI commands
└── db/          # SQLite database
```

## Requirements

- Python 3.10+
- Playwright
- Chromium browser

## License

MIT
