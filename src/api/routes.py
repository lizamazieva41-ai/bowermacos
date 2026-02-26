"""
FastAPI routes for browser control.
"""
import asyncio
import logging
from typing import Optional, List, Any, Dict
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional

from src.browser.manager import BrowserManager, ProfileConfig, BrowserSession

logger = logging.getLogger(__name__)


class ProfileCreate(BaseModel):
    name: str
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    timezone: Optional[str] = None
    language: Optional[str] = None


class NavigateRequest(BaseModel):
    url: str
    timeout: int = 30000


class ClickRequest(BaseModel):
    selector: str
    timeout: int = 5000


class TypeRequest(BaseModel):
    selector: str
    text: str
    timeout: int = 5000


class ScriptRequest(BaseModel):
    script: str


class ScreenshotRequest(BaseModel):
    path: str = "screenshot.png"
    full_page: bool = False


class SessionResponse(BaseModel):
    session_id: str
    profile_name: str
    started_at: str
    status: str


browser_manager: Optional[BrowserManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global browser_manager
    browser_manager = BrowserManager()
    await browser_manager.start()
    logger.info("Browser manager started")
    yield
    await browser_manager.stop()
    logger.info("Browser manager stopped")


app = FastAPI(
    title="Stealth Browser API",
    description="Antidetect Browser System V2 - API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Stealth Browser API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "sessions": len(browser_manager.sessions) if browser_manager else 0}


@app.post("/sessions", response_model=SessionResponse)
async def create_session(profile: ProfileCreate):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    config = ProfileConfig(
        name=profile.name,
        user_agent=profile.user_agent,
        proxy=profile.proxy,
        proxy_username=profile.proxy_username,
        proxy_password=profile.proxy_password,
        headless=profile.headless,
        viewport_width=profile.viewport_width,
        viewport_height=profile.viewport_height,
        timezone=profile.timezone,
        language=profile.language,
    )

    session = await browser_manager.create_session(config)
    return SessionResponse(
        session_id=session.session_id,
        profile_name=session.profile_name,
        started_at=session.started_at.isoformat(),
        status=session.status,
    )


@app.get("/sessions", response_model=List[SessionResponse])
async def list_sessions():
    if not browser_manager:
        return []
    
    sessions = browser_manager.list_sessions()
    return [
        SessionResponse(
            session_id=s.session_id,
            profile_name=s.profile_name,
            started_at=s.started_at.isoformat(),
            status=s.status,
        )
        for s in sessions
    ]


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")
    
    session = browser_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "profile_name": session.profile_name,
        "started_at": session.started_at.isoformat(),
        "status": session.status,
    }


@app.delete("/sessions/{session_id}")
async def close_session(session_id: str):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")
    
    result = await browser_manager.close_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session closed", "session_id": session_id}


@app.post("/sessions/{session_id}/navigate")
async def navigate(session_id: str, request: NavigateRequest):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")
    
    try:
        await browser_manager.navigate(session_id, request.url, request.timeout)
        return {"message": "Navigated", "url": request.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/sessions/{session_id}/click")
async def click(session_id: str, request: ClickRequest):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")
    
    try:
        await browser_manager.click(session_id, request.selector, request.timeout)
        return {"message": "Clicked", "selector": request.selector}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/sessions/{session_id}/type")
async def type_text(session_id: str, request: TypeRequest):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")
    
    try:
        await browser_manager.type_text(session_id, request.selector, request.text, request.timeout)
        return {"message": "Typed", "selector": request.selector, "text": request.text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/sessions/{session_id}/screenshot")
async def screenshot(session_id: str, request: ScreenshotRequest):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")
    
    try:
        await browser_manager.screenshot(session_id, request.path, request.full_page)
        return {"message": "Screenshot saved", "path": request.path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/sessions/{session_id}/execute")
async def execute_script(session_id: str, request: ScriptRequest):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")
    
    try:
        result = await browser_manager.execute_script(session_id, request.script)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
