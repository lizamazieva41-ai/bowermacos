# AGENTS.md - Antidetect Browser Project

## Project Overview

Documentation repository for the Bower Antidetect Browser V2 project. A Python-based application for managing anonymous browser profiles with stealth capabilities.

---

## 1. Build, Lint, and Test Commands

### Python Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Running Tests
```bash
pytest                          # Run all tests
pytest tests/test_browser.py   # Run single test file
pytest tests/test_browser.py::test_launch_headless  # Run single test
pytest -v                      # Verbose output
pytest --cov=src --cov-report=html  # With coverage
```

### Linting & Formatting
```bash
flake8 src/ tests/           # Lint
black --check src/            # Check formatting
black src/                    # Auto-fix formatting
isort --check src/            # Check imports
isort src/                    # Auto-fix imports
mypy src/                     # Type checking
```

### Running the App
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000  # FastAPI
flask run --debug                                    # Flask
```

---

## 2. Code Style Guidelines

### General
- **Python 3.10+** required
- Use **type hints** everywhere
- Follow **PEP 8** with 100 char line limit
- Use **async/await** for I/O-bound operations

### Imports (use isort)
```python
# Standard lib → Third-party → Local
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import pytest
from playwright.async_api import async_playwright
from fastapi import FastAPI

from src.browser.manager import BrowserManager
```

### Naming Conventions
```python
module_name = "browser_manager"  # modules: snake_case
class BrowserSession: pass       # classes: PascalCase
def get_browser_context(): pass  # functions: snake_case
MAX_CONCURRENT_SESSIONS = 50     # constants: UPPER_SNAKE_CASE
def _cleanup_session(self): pass # private: prefix with _
```

### Type Annotations
```python
@dataclass
class ProfileConfig:
    name: str
    user_agent: str
    proxy: Optional[str] = None
    headless: bool = True

def create_session(config: ProfileConfig, timeout: int = 30000) -> BrowserSession:
    ...
```

### Error Handling
Follow error codes from `03_Functional_Specifications/02_Error_Handling.md`:
```python
from enum import IntEnum

class ErrorCode(IntEnum):
    VALIDATION_ERROR = 1001
    NETWORK_ERROR = 2001
    AUTH_ERROR = 3001
    SYSTEM_ERROR = 4001
    SESSION_ERROR = 5001
    PROXY_ERROR = 6001

class BrowserError(Exception):
    def __init__(self, code: int, message: str, details: Optional[Dict] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

raise BrowserError(ErrorCode.SESSION_ERROR, "Browser launch failed", {"reason": "port_in_use"})
```

### Async/Await Patterns
```python
class BrowserManager:
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()
```

### Logging
```python
logger = logging.getLogger(__name__)

def launch_browser(profile: ProfileConfig):
    logger.info(f"Launching browser for profile: {profile.name}")
    try:
        ...
    except Exception as e:
        logger.error(f"Failed to launch browser: {e}", exc_info=True)
        raise
```

### Testing Patterns
```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_browser():
    browser = AsyncMock()
    browser.new_context = AsyncMock()
    return browser

@pytest.mark.asyncio
async def test_create_session(mock_browser):
    config = ProfileConfig(name="test", user_agent="Mozilla/5.0...")
    session = await create_session(config)
    assert session.name == "test"
```

### Expected File Structure
```
/src
  /browser    (manager.py, session.py, context.py)
  /proxy     (loader.py, validator.py)
  /fingerprint (generator.py, spoofers.py)
  /api       (routes.py, models.py)
  /cli       (commands.py)
/tests       (unit/, integration/, e2e/)
```

### Security
- Never commit API keys/tokens
- Use environment variables for secrets
- Validate all user inputs
- Sanitize proxy URLs before use

---

## References
- [Test Plan](./Antidetect_Browser_Documentation/11_Testing_Strategy/01_Test_Plan.md)
- [Error Handling](./Antidetect_Browser_Documentation/03_Functional_Specifications/02_Error_Handling.md)
