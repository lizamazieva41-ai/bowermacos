"""
Performance monitoring module for tracking system and session metrics.
"""
import asyncio
import logging
import time
import psutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class SessionMetrics:
    """Metrics for a single browser session."""
    session_id: str
    profile_name: str
    created_at: datetime
    started_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    navigation_count: int = 0
    click_count: int = 0
    type_count: int = 0
    script_count: int = 0
    total_navigation_time: float = 0.0
    total_click_time: float = 0.0
    total_type_time: float = 0.0
    total_script_time: float = 0.0
    memory_peak_mb: float = 0.0
    errors: List[str] = field(default_factory=list)


@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_used_mb: float
    memory_available_mb: float
    memory_percent: float
    active_sessions: int
    browser_process_count: int
    network_sent_mb: float
    network_recv_mb: float


class PerformanceMonitor:
    """Monitors performance metrics for browser sessions and system resources."""

    def __init__(self, history_size: int = 1000):
        self.session_metrics: Dict[str, SessionMetrics] = {}
        self.system_metrics_history: deque = deque(maxlen=history_size)
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._start_time: Optional[datetime] = None

    async def start(self):
        """Start the performance monitoring."""
        self._monitoring = True
        self._start_time = datetime.now(timezone.utc)
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Performance monitoring started")

    async def stop(self):
        """Stop the performance monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")

    async def _monitor_loop(self):
        """Background task to collect system metrics."""
        interval = 5.0
        while self._monitoring:
            try:
                metrics = await self._collect_system_metrics()
                self.system_metrics_history.append(metrics)
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")

    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        process = psutil.Process()
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        net_io = psutil.net_io_counters()
        
        return SystemMetrics(
            timestamp=datetime.now(timezone.utc),
            cpu_percent=cpu_percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            memory_percent=memory.percent,
            active_sessions=len(self.session_metrics),
            browser_process_count=len([
                p for p in psutil.process_iter(['name']) 
                if 'chrome' in p.info['name'].lower() or 'chromium' in p.info['name'].lower()
            ]),
            network_sent_mb=net_io.bytes_sent / 1024 / 1024,
            network_recv_mb=net_io.bytes_recv / 1024 / 1024,
        )

    def start_session(self, session_id: str, profile_name: str):
        """Record session start."""
        self.session_metrics[session_id] = SessionMetrics(
            session_id=session_id,
            profile_name=profile_name,
            created_at=datetime.now(timezone.utc),
        )
        logger.debug(f"Started tracking metrics for session: {session_id}")

    def end_session(self, session_id: str):
        """Record session end."""
        if session_id in self.session_metrics:
            self.session_metrics[session_id].closed_at = datetime.now(timezone.utc)
            logger.debug(f"Stopped tracking metrics for session: {session_id}")

    def record_navigation(self, session_id: str, duration: float):
        """Record a navigation action."""
        if session_id in self.session_metrics:
            metrics = self.session_metrics[session_id]
            metrics.navigation_count += 1
            metrics.total_navigation_time += duration

    def record_click(self, session_id: str, duration: float):
        """Record a click action."""
        if session_id in self.session_metrics:
            metrics = self.session_metrics[session_id]
            metrics.click_count += 1
            metrics.total_click_time += duration

    def record_type(self, session_id: str, duration: float):
        """Record a type action."""
        if session_id in self.session_metrics:
            metrics = self.session_metrics[session_id]
            metrics.type_count += 1
            metrics.total_type_time += duration

    def record_script_execution(self, session_id: str, duration: float):
        """Record a script execution."""
        if session_id in self.session_metrics:
            metrics = self.session_metrics[session_id]
            metrics.script_count += 1
            metrics.total_script_time += duration

    def record_error(self, session_id: str, error: str):
        """Record an error for a session."""
        if session_id in self.session_metrics:
            self.session_metrics[session_id].errors.append(error)

    def get_session_metrics(self, session_id: str) -> Optional[SessionMetrics]:
        """Get metrics for a specific session."""
        return self.session_metrics.get(session_id)

    def get_all_session_metrics(self) -> List[SessionMetrics]:
        """Get metrics for all sessions."""
        return list(self.session_metrics.values())

    def get_current_system_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics."""
        if self.system_metrics_history:
            return self.system_metrics_history[-1]
        return None

    def get_system_metrics_history(self, limit: int = 100) -> List[SystemMetrics]:
        """Get historical system metrics."""
        return list(self.system_metrics_history)[-limit:]

    def get_uptime(self) -> Optional[float]:
        """Get monitor uptime in seconds."""
        if self._start_time:
            return (datetime.now(timezone.utc) - self._start_time).total_seconds()
        return None

    def get_average_navigation_time(self, session_id: str) -> Optional[float]:
        """Get average navigation time for a session."""
        metrics = self.session_metrics.get(session_id)
        if metrics and metrics.navigation_count > 0:
            return metrics.total_navigation_time / metrics.navigation_count
        return None

    def get_total_errors(self, session_id: str) -> int:
        """Get total error count for a session."""
        metrics = self.session_metrics.get(session_id)
        return len(metrics.errors) if metrics else 0

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        current_system = self.get_current_system_metrics()
        
        active_sessions = [
            m for m in self.session_metrics.values()
            if m.closed_at is None
        ]
        
        return {
            "monitoring_active": self._monitoring,
            "uptime_seconds": self.get_uptime(),
            "total_sessions_tracked": len(self.session_metrics),
            "active_sessions": len(active_sessions),
            "system": {
                "cpu_percent": current_system.cpu_percent if current_system else 0,
                "memory_used_mb": current_system.memory_used_mb if current_system else 0,
                "memory_percent": current_system.memory_percent if current_system else 0,
                "browser_processes": current_system.browser_process_count if current_system else 0,
            } if current_system else None,
        }


performance_monitor = PerformanceMonitor()
