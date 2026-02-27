"""
WebSocket Client for Real-time GUI Updates
"""

import threading
import json
import logging
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket client for real-time communication with the API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.replace("http", "ws")
        self.ws: Optional[Any] = None
        self.connected = False
        self.session_id: Optional[str] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        
        self._callbacks: Dict[str, List[Callable]] = {
            "connect": [],
            "disconnect": [],
            "message": [],
            "error": [],
            "console": [],
            "session_update": [],
        }
    
    def connect(self, session_id: str) -> bool:
        """Connect to a session's WebSocket."""
        if self.connected:
            self.disconnect()
        
        self.session_id = session_id
        url = f"{self.base_url}/ws/session/{session_id}"
        
        try:
            import websocket
            
            self.ws = websocket.WebSocketApp(
                url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )
            
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            
            return True
        except ImportError:
            logger.warning("websocket-client not installed, using polling fallback")
            return self._start_polling(session_id)
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            self._trigger_callback("error", {"error": str(e)})
            return False
    
    def _run(self):
        """Run WebSocket in thread."""
        try:
            self.ws.run_forever(ping_interval=30, ping_timeout=10)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
    
    def _start_polling(self, session_id: str) -> bool:
        """Fallback to polling if WebSocket not available."""
        self.session_id = session_id
        self._running = True
        self.connected = True
        self._trigger_callback("connect", {"session_id": session_id})
        
        self._thread = threading.Thread(target=self._poll_session, daemon=True)
        self._thread.start()
        return True
    
    def _poll_session(self):
        """Poll session status as fallback."""
        import time
        import urllib.request
        import urllib.error
        
        while self._running:
            try:
                if self.session_id and self.base_url:
                    url = f"{self.base_url.replace('ws', 'http')}/api/v1/sessions/{self.session_id}"
                    req = urllib.request.Request(url)
                    
                    try:
                        with urllib.request.urlopen(req, timeout=5) as response:
                            data = json.loads(response.read().decode())
                            self._trigger_callback("session_update", data)
                    except:
                        pass
                
                time.sleep(2)
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(5)
    
    def _on_open(self, ws):
        """WebSocket opened."""
        self.connected = True
        logger.info(f"WebSocket connected to session: {self.session_id}")
        self._trigger_callback("connect", {"session_id": self.session_id})
    
    def _on_message(self, ws, message: str):
        """Handle incoming message."""
        try:
            data = json.loads(message)
            msg_type = data.get("type", "message")
            
            if msg_type == "console":
                self._trigger_callback("console", data.get("data", {}))
            elif msg_type == "session_update":
                self._trigger_callback("session_update", data.get("data", {}))
            else:
                self._trigger_callback("message", data)
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON: {message}")
    
    def _on_error(self, ws, error):
        """WebSocket error."""
        logger.error(f"WebSocket error: {error}")
        self._trigger_callback("error", {"error": str(error)})
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket closed."""
        self.connected = False
        logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")
        self._trigger_callback("disconnect", {"code": close_status_code, "message": close_msg})
    
    def disconnect(self):
        """Disconnect from WebSocket."""
        self._running = False
        
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            self.ws = None
        
        self.connected = False
        self.session_id = None
    
    def send(self, command: str, params: Dict[str, Any] = None):
        """Send command to server."""
        if not self.connected or not self.ws:
            logger.warning("WebSocket not connected")
            return False
        
        try:
            data = {
                "command": command,
                "params": params or {}
            }
            self.ws.send(json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def on(self, event: str, callback: Callable):
        """Register callback for event."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def off(self, event: str, callback: Callable):
        """Unregister callback."""
        if event in self._callbacks and callback in self._callbacks[event]:
            self._callbacks[event].remove(callback)
    
    def _trigger_callback(self, event: str, data: Any):
        """Trigger all callbacks for an event."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")


class RealTimeManager:
    """Manager for real-time updates across the application."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_clients: Dict[str, WebSocketClient] = {}
        self._session_callbacks: Dict[str, List[Callable]] = {}
    
    def connect_session(self, session_id: str) -> WebSocketClient:
        """Connect to a session for real-time updates."""
        if session_id in self.ws_clients:
            self.ws_clients[session_id].disconnect()
        
        client = WebSocketClient(self.base_url)
        client.connect(session_id)
        
        def handle_update(data):
            self._notify_session_callbacks(session_id, data)
        
        client.on("session_update", handle_update)
        client.on("console", handle_update)
        
        self.ws_clients[session_id] = client
        return client
    
    def disconnect_session(self, session_id: str):
        """Disconnect from a session."""
        if session_id in self.ws_clients:
            self.ws_clients[session_id].disconnect()
            del self.ws_clients[session_id]
    
    def disconnect_all(self):
        """Disconnect all sessions."""
        for client in self.ws_clients.values():
            client.disconnect()
        self.ws_clients.clear()
    
    def register_session_callback(self, session_id: str, callback: Callable):
        """Register callback for session updates."""
        if session_id not in self._session_callbacks:
            self._session_callbacks[session_id] = []
        self._session_callbacks[session_id].append(callback)
    
    def unregister_session_callback(self, session_id: str, callback: Callable):
        """Unregister session callback."""
        if session_id in self._session_callbacks:
            if callback in self._session_callbacks[session_id]:
                self._session_callbacks[session_id].remove(callback)
    
    def _notify_session_callbacks(self, session_id: str, data: Any):
        """Notify all callbacks for a session."""
        for callback in self._session_callbacks.get(session_id, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Session callback error: {e}")
    
    def get_connected_sessions(self) -> List[str]:
        """Get list of connected session IDs."""
        return [
            sid for sid, client in self.ws_clients.items()
            if client.connected
        ]


rt_manager = RealTimeManager()
