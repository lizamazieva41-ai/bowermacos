"""
FastAPI routes for browser control - v1 API.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Request,
    WebSocket,
    WebSocketDisconnect,
    Depends,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.api.schemas import ApiResponse, ProfileResponse, ProfileListResponse
from src.api.errors import ErrorCode
from src.api.middleware import AuditMiddleware
from src.api.auth import get_current_user
from src.browser.manager import BrowserManager, ProfileConfig
from src.browser.recovery import session_recovery_service
from src.db.store import Database
from src.monitoring import performance_monitor
from src.proxy.validator import validate_proxy_endpoint

logger = logging.getLogger(__name__)


class ProfileCreate(BaseModel):
    name: str
    use_case: Optional[str] = None
    browser_engine: str = "chromium"
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    resolution: str = "1920x1080"
    timezone: Optional[str] = None
    language: Optional[str] = None
    headless: bool = True
    advanced_settings: Optional[str] = None


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    use_case: Optional[str] = None
    browser_engine: Optional[str] = None
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    resolution: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    headless: Optional[bool] = None
    advanced_settings: Optional[str] = None


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
database: Optional[Database] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global browser_manager, database
    database = Database()
    await database.init_db()
    browser_manager = BrowserManager()
    await browser_manager.start()

    from src.api.middleware import audit_logger
    audit_logger.set_database(database)

    session_recovery_service.set_browser_manager(browser_manager)
    await session_recovery_service.start()

    await performance_monitor.start()

    logger.info("Browser manager, recovery service, and monitoring started")
    yield

    await performance_monitor.stop()
    await session_recovery_service.stop()
    await browser_manager.stop()
    await database.close()
    logger.info("All services stopped")


app = FastAPI(
    title="Stealth Browser API",
    description="Antidetect Browser System V2 - API",
    version="1.0.0",
    lifespan=lifespan,
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(AuditMiddleware)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest):
    from src.api.auth import login as auth_login

    result = await auth_login(login_data.username, login_data.password)
    if result:
        return ApiResponse.ok(data=result.model_dump(), message="Login successful")
    return ApiResponse.error(code=401, message="Invalid credentials")


@app.get("/api/v1/auth/api-key")
@limiter.limit("3/minute")
async def create_api_key(request: Request, name: str, days_valid: int = 365):
    from src.api.auth import generate_api_key

    key = generate_api_key(name, days_valid)
    return ApiResponse.ok(
        data={"api_key": key, "name": name}, message="API key created"
    )


@app.get("/")
async def root():
    return {"message": "Stealth Browser API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "sessions": len(browser_manager.sessions) if browser_manager else 0,
    }


@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard UI."""
    from pathlib import Path

    dashboard_path = (
        Path(__file__).parent.parent.parent / "ui" / "dashboard" / "index.html"
    )
    return FileResponse(dashboard_path)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections.values():
            await connection.send_json(message)


ws_manager = ConnectionManager()


@app.websocket("/ws/session/{session_id}")
async def websocket_session(websocket: WebSocket, session_id: str):
    if not browser_manager:
        await websocket.close(code=1011, reason="Browser manager not initialized")
        return

    session = browser_manager.get_session(session_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return

    await ws_manager.connect(session_id, websocket)

    page = session.page

    console_messages = []
    page_errors = []

    def handle_console_msg(msg):
        console_messages.append(
            {
                "type": msg.type,
                "text": msg.text,
                "timestamp": datetime.now().isoformat(),
            }
        )
        asyncio.create_task(
            ws_manager.send_message(
                session_id,
                {"type": "console", "data": {"type": msg.type, "text": msg.text}},
            )
        )

    def handle_page_error(error):
        page_errors.append(
            {"error": str(error), "timestamp": datetime.now().isoformat()}
        )
        asyncio.create_task(
            ws_manager.send_message(
                session_id, {"type": "error", "data": {"error": str(error)}}
            )
        )

    page.on("console", handle_console_msg)
    page.on("pageerror", handle_page_error)

    try:
        await ws_manager.send_message(
            session_id,
            {
                "type": "connected",
                "data": {
                    "session_id": session_id,
                    "profile_name": session.profile_name,
                },
            },
        )

        while True:
            data = await websocket.receive_json()
            command = data.get("command")
            params = data.get("params", {})

            try:
                result = await _handle_ws_command(session_id, command, params)
                await ws_manager.send_message(
                    session_id, {"type": "success", "command": command, "data": result}
                )
            except Exception as e:
                await ws_manager.send_message(
                    session_id,
                    {"type": "error", "command": command, "data": {"error": str(e)}},
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    finally:
        ws_manager.disconnect(session_id)
        page.remove_listener("console", handle_console_msg)
        page.remove_listener("pageerror", handle_page_error)


async def _handle_ws_command(
    session_id: str, command: str, params: Dict[str, Any]
) -> Any:
    session = browser_manager.get_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    page = session.page

    if command == "navigate":
        url = params.get("url")
        timeout = params.get("timeout", 30000)
        await page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        return {"url": url}

    elif command == "click":
        selector = params.get("selector")
        timeout = params.get("timeout", 5000)
        await page.click(selector, timeout=timeout)
        return {"selector": selector}

    elif command == "type":
        selector = params.get("selector")
        text = params.get("text")
        timeout = params.get("timeout", 5000)
        await page.fill(selector, text, timeout=timeout)
        return {"selector": selector, "text": text}

    elif command == "screenshot":
        path = params.get("path", "screenshot.png")
        full_page = params.get("full_page", False)
        await page.screenshot(path=path, full_page=full_page)
        return {"path": path}

    elif command == "execute":
        script = params.get("script")
        return await page.evaluate(script)

    elif command == "evaluate":
        selector = params.get("selector")
        return await page.evaluate(f"document.querySelector('{selector}')")

    elif command == "get_html":
        selector = params.get("selector")
        if selector:
            return await page.evaluate(
                f"document.querySelector('{selector}').innerHTML"
            )
        return await page.content()

    elif command == "get_title":
        return await page.title()

    elif command == "get_url":
        return page.url

    elif command == "wait_for_selector":
        selector = params.get("selector")
        timeout = params.get("timeout", 30000)
        await page.wait_for_selector(selector, timeout=timeout)
        return {"selector": selector}

    elif command == "wait_for_navigation":
        timeout = params.get("timeout", 30000)
        await page.wait_for_load_state("networkidle", timeout=timeout)
        return {"url": page.url}

    elif command == "go_back":
        await page.go_back()
        return {"url": page.url}

    elif command == "go_forward":
        await page.go_forward()
        return {"url": page.url}

    elif command == "reload":
        timeout = params.get("timeout", 30000)
        await page.reload(timeout=timeout)
        return {"url": page.url}

    else:
        raise ValueError(f"Unknown command: {command}")


def _profile_from_db_to_response(profile) -> ProfileResponse:
    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        use_case=profile.use_case,
        browser_engine=profile.browser_engine,
        user_agent=profile.user_agent,
        proxy=profile.proxy,
        proxy_username=profile.proxy_username,
        proxy_password=profile.proxy_password,
        resolution=profile.resolution,
        timezone=profile.timezone,
        language=profile.language,
        headless=profile.headless,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@app.get("/api/v1/profiles", dependencies=[Depends(get_current_user)])
@limiter.limit("100/minute")
async def list_profiles(request: Request) -> ApiResponse:
    profiles = await database.list_profiles()
    return ApiResponse.ok(
        data=ProfileListResponse(
            profiles=[_profile_from_db_to_response(p) for p in profiles],
            total=len(profiles),
        ).model_dump()
    )


@app.post(
    "/api/v1/profiles",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("50/minute")
async def create_profile(request: Request, profile: ProfileCreate) -> ApiResponse:
    existing = await database.get_profile_by_name(profile.name)
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Profile with name '{profile.name}' already exists"
        )

    profile_data = profile.model_dump()
    db_profile = await database.create_profile(profile_data)
    return ApiResponse.ok(
        data=_profile_from_db_to_response(db_profile).model_dump(),
        message="Profile created successfully",
    )


@app.get("/api/v1/profiles/{profile_id}", dependencies=[Depends(get_current_user)])
async def get_profile(profile_id: int) -> ApiResponse:
    profile = await database.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")
    return ApiResponse.ok(data=_profile_from_db_to_response(profile).model_dump())


@app.put("/api/v1/profiles/{profile_id}", dependencies=[Depends(get_current_user)])
async def update_profile(profile_id: int, profile: ProfileUpdate) -> ApiResponse:
    update_data = {k: v for k, v in profile.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    updated = await database.update_profile(profile_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    return ApiResponse.ok(
        data=_profile_from_db_to_response(updated).model_dump(),
        message="Profile updated successfully",
    )


@app.delete("/api/v1/profiles/{profile_id}", dependencies=[Depends(get_current_user)])
async def delete_profile(profile_id: int) -> ApiResponse:
    success = await database.delete_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")
    return ApiResponse.ok(message="Profile deleted successfully")


class ProfileCloneRequest(BaseModel):
    name: str


@app.post(
    "/api/v1/profiles/{profile_id}/clone",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("20/minute")
async def clone_profile(
    request: Request,
    profile_id: int,
    clone_request: ProfileCloneRequest,
) -> ApiResponse:
    source_profile = await database.get_profile(profile_id)
    if not source_profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    existing = await database.get_profile_by_name(clone_request.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Profile with name '{clone_request.name}' already exists",
        )

    clone_data = {
        "name": clone_request.name,
        "use_case": source_profile.use_case,
        "browser_engine": source_profile.browser_engine,
        "user_agent": source_profile.user_agent,
        "proxy": source_profile.proxy,
        "proxy_username": source_profile.proxy_username,
        "proxy_password": source_profile.proxy_password,
        "resolution": source_profile.resolution,
        "timezone": source_profile.timezone,
        "language": source_profile.language,
        "headless": source_profile.headless,
        "advanced_settings": source_profile.advanced_settings,
    }

    new_profile = await database.create_profile(clone_data)
    return ApiResponse.ok(
        data=_profile_from_db_to_response(new_profile).model_dump(),
        message="Profile cloned successfully",
    )


@app.get(
    "/api/v1/profiles/{profile_id}/export",
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("30/minute")
async def export_profile(request: Request, profile_id: int) -> ApiResponse:
    profile = await database.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    export_data = {
        "name": profile.name,
        "use_case": profile.use_case,
        "browser_engine": profile.browser_engine,
        "user_agent": profile.user_agent,
        "proxy": profile.proxy,
        "proxy_username": profile.proxy_username,
        "resolution": profile.resolution,
        "timezone": profile.timezone,
        "language": profile.language,
        "headless": profile.headless,
        "advanced_settings": profile.advanced_settings,
    }

    return ApiResponse.ok(
        data=export_data,
        message="Profile exported successfully",
    )


@app.post(
    "/api/v1/profiles/import",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("20/minute")
async def import_profile(request: Request, profile: ProfileCreate) -> ApiResponse:
    existing = await database.get_profile_by_name(profile.name)
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Profile with name '{profile.name}' already exists"
        )

    profile_data = profile.model_dump()
    db_profile = await database.create_profile(profile_data)
    return ApiResponse.ok(
        data=_profile_from_db_to_response(db_profile).model_dump(),
        message="Profile imported successfully",
    )


@app.get(
    "/api/v1/sessions/{session_id}/page-source",
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("60/minute")
async def get_page_source(request: Request, session_id: str) -> ApiResponse:
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    session = browser_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        page_source = await session.page.content()
        return ApiResponse.ok(
            data={"page_source": page_source},
            message="Page source retrieved successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/api/v1/sessions",
    response_model=SessionResponse,
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("30/minute")
async def create_session(
    request: Request,
    profile_id: Optional[int] = None,
    profile: Optional[ProfileCreate] = None,
):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    config_data = {}

    if profile_id is not None:
        db_profile = await database.get_profile(profile_id)
        if not db_profile:
            raise HTTPException(
                status_code=404, detail=f"Profile {profile_id} not found"
            )
        config_data = {
            "name": db_profile.name,
            "user_agent": db_profile.user_agent,
            "proxy": db_profile.proxy,
            "proxy_username": db_profile.proxy_username,
            "proxy_password": db_profile.proxy_password,
            "headless": db_profile.headless,
            "viewport_width": (
                int(db_profile.resolution.split("x")[0])
                if "x" in db_profile.resolution
                else 1920
            ),
            "viewport_height": (
                int(db_profile.resolution.split("x")[1])
                if "x" in db_profile.resolution
                else 1080
            ),
            "timezone": db_profile.timezone,
            "language": db_profile.language,
        }
    elif profile:
        config_data = {
            "name": profile.name,
            "user_agent": profile.user_agent,
            "proxy": profile.proxy,
            "proxy_username": profile.proxy_username,
            "proxy_password": profile.proxy_password,
            "headless": profile.headless,
        }
    else:
        raise HTTPException(
            status_code=400, detail="Either profile_id or profile data required"
        )

    config = ProfileConfig(**config_data)
    session = await browser_manager.create_session(config)

    session_recovery_service.register_session(session.session_id, config_data)
    performance_monitor.start_session(session.session_id, session.profile_name)

    if database:
        await database.create_session_record(
            {
                "profile_id": profile_id or 0,
                "session_id": session.session_id,
                "status": "active",
            }
        )

    return SessionResponse(
        session_id=session.session_id,
        profile_name=session.profile_name,
        started_at=session.started_at.isoformat(),
        status=session.status,
    )


@app.get(
    "/api/v1/sessions",
    response_model=List[SessionResponse],
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("60/minute")
async def list_sessions(request: Request):
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


@app.get("/api/v1/sessions/{session_id}", dependencies=[Depends(get_current_user)])
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


@app.delete("/api/v1/sessions/{session_id}", dependencies=[Depends(get_current_user)])
async def close_session(session_id: str):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    result = await browser_manager.close_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")

    session_recovery_service.unregister_session(session_id)
    performance_monitor.end_session(session_id)

    return {"message": "Session closed", "session_id": session_id}


@app.post(
    "/api/v1/sessions/{session_id}/start", dependencies=[Depends(get_current_user)]
)
async def start_session(session_id: str):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    session = browser_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == "active":
        return ApiResponse.ok(message="Session already running")

    session.status = "active"
    return ApiResponse.ok(message="Session started")


@app.post(
    "/api/v1/sessions/{session_id}/stop", dependencies=[Depends(get_current_user)]
)
async def stop_session(session_id: str):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    result = await browser_manager.close_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")

    return ApiResponse.ok(message="Session stopped")


@app.post(
    "/api/v1/sessions/{session_id}/navigate", dependencies=[Depends(get_current_user)]
)
async def navigate(session_id: str, request: NavigateRequest):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    try:
        await browser_manager.navigate(session_id, request.url, request.timeout)
        return ApiResponse.ok(message="Navigated", data={"url": request.url})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/api/v1/sessions/{session_id}/click", dependencies=[Depends(get_current_user)]
)
async def click(session_id: str, request: ClickRequest):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    try:
        await browser_manager.click(session_id, request.selector, request.timeout)
        return ApiResponse.ok(message="Clicked", data={"selector": request.selector})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/api/v1/sessions/{session_id}/type", dependencies=[Depends(get_current_user)]
)
async def type_text(session_id: str, request: TypeRequest):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    try:
        await browser_manager.type_text(
            session_id, request.selector, request.text, request.timeout
        )
        return ApiResponse.ok(
            message="Typed", data={"selector": request.selector, "text": request.text}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/api/v1/sessions/{session_id}/screenshot", dependencies=[Depends(get_current_user)]
)
async def screenshot(session_id: str, request: ScreenshotRequest):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    try:
        await browser_manager.screenshot(session_id, request.path, request.full_page)
        return ApiResponse.ok(message="Screenshot saved", data={"path": request.path})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/api/v1/sessions/{session_id}/execute", dependencies=[Depends(get_current_user)]
)
async def execute_script(session_id: str, request: ScriptRequest):
    if not browser_manager:
        raise HTTPException(status_code=500, detail="Browser manager not initialized")

    try:
        result = await browser_manager.execute_script(session_id, request.script)
        return ApiResponse.ok(data={"result": result})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/proxy/validate", dependencies=[Depends(get_current_user)])
async def validate_proxy(proxy: str):
    result = await validate_proxy_endpoint(proxy)
    if result.get("valid"):
        return ApiResponse.ok(data=result, message="Proxy is valid")
    return ApiResponse.error(
        code=ErrorCode.PROXY_ERROR,
        message=result.get("message", "Proxy validation failed"),
        details=result,
    )


@app.get("/api/v1/metrics", dependencies=[Depends(get_current_user)])
async def get_metrics():
    """Get performance metrics."""
    return performance_monitor.get_summary()


@app.get("/api/v1/recovery/status", dependencies=[Depends(get_current_user)])
async def get_recovery_status():
    """Get session recovery status."""
    return session_recovery_service.get_recovery_summary()


class ProxyCreate(BaseModel):
    name: str
    proxy_type: str = "http"
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: bool = True


class ProxyUpdate(BaseModel):
    name: Optional[str] = None
    proxy_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class ProxyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    proxy_type: str
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProxyListResponse(BaseModel):
    proxies: list[ProxyResponse]
    total: int


def _proxy_from_db_to_response(proxy) -> ProxyResponse:
    return ProxyResponse(
        id=proxy.id,
        name=proxy.name,
        proxy_type=proxy.proxy_type,
        host=proxy.host,
        port=proxy.port,
        username=proxy.username,
        password=proxy.password,
        is_active=proxy.is_active,
        created_at=proxy.created_at,
        updated_at=proxy.updated_at,
    )


@app.get("/api/v1/proxies", dependencies=[Depends(get_current_user)])
@limiter.limit("60/minute")
async def list_proxies(request: Request) -> ApiResponse:
    proxies = await database.list_proxies()
    return ApiResponse.ok(
        data=ProxyListResponse(
            proxies=[_proxy_from_db_to_response(p) for p in proxies],
            total=len(proxies),
        ).model_dump()
    )


@app.post(
    "/api/v1/proxies",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("30/minute")
async def create_proxy(request: Request, proxy: ProxyCreate) -> ApiResponse:
    proxy_data = proxy.model_dump()
    db_proxy = await database.create_proxy(proxy_data)
    return ApiResponse.ok(
        data=_proxy_from_db_to_response(db_proxy).model_dump(),
        message="Proxy created successfully",
    )


@app.get("/api/v1/proxies/{proxy_id}", dependencies=[Depends(get_current_user)])
async def get_proxy(proxy_id: int) -> ApiResponse:
    proxy = await database.get_proxy(proxy_id)
    if not proxy:
        raise HTTPException(status_code=404, detail=f"Proxy {proxy_id} not found")
    return ApiResponse.ok(data=_proxy_from_db_to_response(proxy).model_dump())


@app.put("/api/v1/proxies/{proxy_id}", dependencies=[Depends(get_current_user)])
async def update_proxy(proxy_id: int, proxy: ProxyUpdate) -> ApiResponse:
    update_data = {k: v for k, v in proxy.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    updated = await database.update_proxy(proxy_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Proxy {proxy_id} not found")

    return ApiResponse.ok(
        data=_proxy_from_db_to_response(updated).model_dump(),
        message="Proxy updated successfully",
    )


@app.delete("/api/v1/proxies/{proxy_id}", dependencies=[Depends(get_current_user)])
async def delete_proxy(proxy_id: int) -> ApiResponse:
    success = await database.delete_proxy(proxy_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Proxy {proxy_id} not found")
    return ApiResponse.ok(message="Proxy deleted successfully")


@app.post("/api/v1/proxies/{proxy_id}/test", dependencies=[Depends(get_current_user)])
@limiter.limit("10/minute")
async def test_proxy(request: Request, proxy_id: int) -> ApiResponse:
    proxy = await database.get_proxy(proxy_id)
    if not proxy:
        raise HTTPException(status_code=404, detail=f"Proxy {proxy_id} not found")

    proxy_url = f"{proxy.proxy_type}://{proxy.host}:{proxy.port}"
    if proxy.username and proxy.password:
        proxy_url = (
            f"{proxy.proxy_type}://{proxy.username}:{proxy.password}"
            f"@{proxy.host}:{proxy.port}"
        )

    result = await validate_proxy_endpoint(proxy_url)
    if result.get("valid"):
        return ApiResponse.ok(data=result, message="Proxy is working")
    return ApiResponse.error(
        code=ErrorCode.PROXY_ERROR,
        message=result.get("message", "Proxy test failed"),
        details=result,
    )


@app.get("/api/v1/proxies/health", dependencies=[Depends(get_current_user)])
async def get_proxy_health() -> ApiResponse:
    from src.proxy.health_monitor import proxy_health_monitor

    health = proxy_health_monitor.get_health_summary()
    return ApiResponse.ok(data=health)
