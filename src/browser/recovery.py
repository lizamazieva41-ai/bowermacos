"""
Auto-recovery system for crashed browser sessions.
Monitors sessions and automatically restarts failed sessions.
"""
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional, Callable, Awaitable
from enum import Enum

logger = logging.getLogger(__name__)


class SessionState(Enum):
    ACTIVE = "active"
    CRASHED = "crashed"
    RECOVERING = "recovering"
    CLOSED = "closed"


@dataclass
class SessionRecoveryConfig:
    max_recovery_attempts: int = 3
    recovery_delay_seconds: int = 5
    health_check_interval: int = 30
    enable_auto_recovery: bool = True


@dataclass
class SessionStatus:
    session_id: str
    state: SessionState
    last_check: datetime
    recovery_attempts: int = 0
    last_error: Optional[str] = None


class SessionRecoveryService:
    def __init__(
        self,
        config: Optional[SessionRecoveryConfig] = None,
    ):
        self.config = config or SessionRecoveryConfig()
        self.session_status: Dict[str, SessionStatus] = {}
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._browser_manager = None
        self._profile_configs: Dict[str, dict] = {}

    def set_browser_manager(self, browser_manager):
        """Set the browser manager for recovery operations."""
        self._browser_manager = browser_manager

    def register_session(
        self,
        session_id: str,
        profile_config: dict,
    ):
        """Register a session for monitoring and recovery."""
        self.session_status[session_id] = SessionStatus(
            session_id=session_id,
            state=SessionState.ACTIVE,
            last_check=datetime.now(timezone.utc),
        )
        self._profile_configs[session_id] = profile_config
        logger.info(f"Registered session for recovery monitoring: {session_id}")

    def unregister_session(self, session_id: str):
        """Unregister a session from recovery monitoring."""
        if session_id in self.session_status:
            del self.session_status[session_id]
        if session_id in self._profile_configs:
            del self._profile_configs[session_id]
        logger.info(f"Unregistered session from recovery: {session_id}")

    async def start(self):
        """Start the session recovery monitoring."""
        if not self.config.enable_auto_recovery:
            logger.info("Auto-recovery is disabled")
            return

        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Session recovery monitoring started")

    async def stop(self):
        """Stop the session recovery monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Session recovery monitoring stopped")

    async def _monitor_loop(self):
        """Background task to monitor session health."""
        while self._monitoring:
            try:
                await self._check_all_sessions()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session recovery monitoring: {e}")
                await asyncio.sleep(self.config.health_check_interval)

    async def _check_all_sessions(self):
        """Check health of all registered sessions."""
        for session_id in list(self.session_status.keys()):
            await self._check_session_health(session_id)

    async def _check_session_health(self, session_id: str):
        """Check health of a single session."""
        status = self.session_status.get(session_id)
        if not status or status.state == SessionState.CLOSED:
            return

        status.last_check = datetime.now()

        if not self._browser_manager:
            logger.warning("Browser manager not set, skipping health check")
            return

        try:
            session = self._browser_manager.get_session(session_id)
            if session is None:
                await self._handle_session_crash(session_id)
            elif session.status == "closed":
                await self._handle_session_crash(session_id)
            else:
                status.state = SessionState.ACTIVE
                status.last_error = None
        except Exception as e:
            logger.error(f"Error checking session {session_id}: {e}")
            await self._handle_session_crash(session_id)

    async def _handle_session_crash(self, session_id: str):
        """Handle a crashed session."""
        status = self.session_status.get(session_id)
        if not status:
            return

        status.state = SessionState.CRASHED
        status.recovery_attempts += 1
        status.last_error = "Session crashed or closed unexpectedly"

        logger.warning(
            f"Session {session_id} crashed (attempt {status.recovery_attempts}/"
            f"{self.config.max_recovery_attempts})"
        )

        if status.recovery_attempts <= self.config.max_recovery_attempts:
            await self._recover_session(session_id)
        else:
            logger.error(
                f"Session {session_id} exceeded max recovery attempts, marking as closed"
            )
            status.state = SessionState.CLOSED
            self.unregister_session(session_id)

    async def _recover_session(self, session_id: str):
        """Attempt to recover a crashed session."""
        status = self.session_status.get(session_id)
        profile_config = self._profile_configs.get(session_id)

        if not status or not profile_config:
            return

        status.state = SessionState.RECOVERING

        logger.info(f"Attempting to recover session {session_id}")

        await asyncio.sleep(self.config.recovery_delay_seconds)

        try:
            from src.browser.manager import ProfileConfig

            config = ProfileConfig(**profile_config)
            new_session = await self._browser_manager.create_session(config)

            if new_session.session_id != session_id:
                old_session = self._browser_manager.sessions.pop(new_session.session_id, None)
                if old_session:
                    self._browser_manager.sessions[session_id] = old_session
                    new_session.session_id = session_id
                    self._profile_configs[session_id] = self._profile_configs.pop(new_session.session_id, profile_config)

            old_status = self.session_status.get(session_id)
            if old_status:
                old_status.state = SessionState.ACTIVE
                old_status.recovery_attempts = 0

            logger.info(f"Successfully recovered session {session_id}")

        except Exception as e:
            logger.error(f"Failed to recover session {session_id}: {e}")
            status.last_error = str(e)

    async def force_recovery(self, session_id: str) -> bool:
        """Force immediate recovery of a session."""
        status = self.session_status.get(session_id)
        if not status:
            logger.warning(f"Session {session_id} not registered")
            return False

        await self._recover_session(session_id)
        return True

    def get_session_status(self, session_id: str) -> Optional[SessionStatus]:
        """Get status of a specific session."""
        return self.session_status.get(session_id)

    def get_all_session_statuses(self) -> Dict[str, SessionStatus]:
        """Get status of all monitored sessions."""
        return self.session_status.copy()

    def get_recovery_summary(self) -> Dict:
        """Get a summary of recovery status."""
        total = len(self.session_status)
        active = sum(1 for s in self.session_status.values() if s.state == SessionState.ACTIVE)
        crashed = sum(1 for s in self.session_status.values() if s.state == SessionState.CRASHED)
        recovering = sum(1 for s in self.session_status.values() if s.state == SessionState.RECOVERING)
        closed = sum(1 for s in self.session_status.values() if s.state == SessionState.CLOSED)

        return {
            "total_monitored": total,
            "active": active,
            "crashed": crashed,
            "recovering": recovering,
            "closed": closed,
            "auto_recovery_enabled": self.config.enable_auto_recovery,
        }


session_recovery_service = SessionRecoveryService()
