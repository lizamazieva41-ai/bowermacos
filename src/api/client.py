"""
HTTP Client for interacting with the Stealth Browser API.
"""

import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class SessionInfo:
    session_id: str
    profile_name: str
    started_at: str
    status: str


@dataclass
class ProfileInfo:
    id: int
    name: str
    use_case: Optional[str]
    browser_engine: str
    user_agent: Optional[str]
    proxy: Optional[str]
    headless: bool


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)

    def close(self):
        self.client.close()

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_profiles(self) -> List[ProfileInfo]:
        result = self._request("GET", "/api/v1/profiles")
        if result.get("success"):
            data = result.get("data", {})
            profiles = data.get("profiles", [])
            return [ProfileInfo(**p) for p in profiles]
        return []

    def get_profile(self, profile_id: int) -> Optional[ProfileInfo]:
        result = self._request("GET", f"/api/v1/profiles/{profile_id}")
        if result.get("success"):
            return ProfileInfo(**result.get("data", {}))
        return None

    def create_profile(self, profile_data: Dict) -> Optional[ProfileInfo]:
        result = self._request("POST", "/api/v1/profiles", json=profile_data)
        if result.get("success"):
            return ProfileInfo(**result.get("data", {}))
        return None

    def update_profile(
        self, profile_id: int, profile_data: Dict
    ) -> Optional[ProfileInfo]:
        result = self._request(
            "PUT", f"/api/v1/profiles/{profile_id}", json=profile_data
        )
        if result.get("success"):
            return ProfileInfo(**result.get("data", {}))
        return None

    def delete_profile(self, profile_id: int) -> bool:
        result = self._request("DELETE", f"/api/v1/profiles/{profile_id}")
        return result.get("success", False)

    def create_session(
        self, profile_id: Optional[int] = None, profile_data: Optional[Dict] = None
    ) -> Optional[SessionInfo]:
        kwargs = {}
        if profile_id:
            kwargs["params"] = {"profile_id": profile_id}
        if profile_data:
            kwargs["json"] = profile_data
        result = self._request("POST", "/api/v1/sessions", **kwargs)
        if result.get("success") or "session_id" in result:
            return SessionInfo(**result)
        return None

    def list_sessions(self) -> List[SessionInfo]:
        result = self._request("GET", "/api/v1/sessions")
        return [SessionInfo(**s) for s in result]

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        result = self._request("GET", f"/api/v1/sessions/{session_id}")
        if result:
            return SessionInfo(**result)
        return None

    def close_session(self, session_id: str) -> bool:
        result = self._request("DELETE", f"/api/v1/sessions/{session_id}")
        return result.get("success", False)

    def navigate(self, session_id: str, url: str) -> bool:
        result = self._request(
            "POST", f"/api/v1/sessions/{session_id}/navigate", json={"url": url}
        )
        return result.get("success", False)

    def click(self, session_id: str, selector: str) -> bool:
        result = self._request(
            "POST", f"/api/v1/sessions/{session_id}/click", json={"selector": selector}
        )
        return result.get("success", False)

    def type_text(self, session_id: str, selector: str, text: str) -> bool:
        result = self._request(
            "POST",
            f"/api/v1/sessions/{session_id}/type",
            json={"selector": selector, "text": text},
        )
        return result.get("success", False)

    def screenshot(self, session_id: str, path: str = "screenshot.png") -> bool:
        result = self._request(
            "POST", f"/api/v1/sessions/{session_id}/screenshot", json={"path": path}
        )
        return result.get("success", False)

    def execute_script(self, session_id: str, script: str) -> Any:
        result = self._request(
            "POST", f"/api/v1/sessions/{session_id}/execute", json={"script": script}
        )
        if result.get("success"):
            return result.get("data", {}).get("result")
        return None

    def health_check(self) -> Dict[str, Any]:
        result = self._request("GET", "/health")
        return result

    def validate_proxy(self, proxy: str) -> Dict[str, Any]:
        result = self._request("GET", "/api/v1/proxy/validate", params={"proxy": proxy})
        return result.get("data", {})

    def clone_profile(self, profile_id: int, new_name: str) -> Optional[ProfileInfo]:
        result = self._request(
            "POST",
            f"/api/v1/profiles/{profile_id}/clone",
            json={"name": new_name},
        )
        if result.get("success"):
            return ProfileInfo(**result.get("data", {}))
        return None

    def export_profile(self, profile_id: int) -> Optional[Dict[str, Any]]:
        result = self._request("GET", f"/api/v1/profiles/{profile_id}/export")
        if result.get("success"):
            return result
        return None

    def import_profile(self, profile_data: Dict) -> Optional[ProfileInfo]:
        result = self._request("POST", "/api/v1/profiles/import", json=profile_data)
        if result.get("success"):
            return ProfileInfo(**result.get("data", {}))
        return None

    def get_page_source(self, session_id: str) -> Optional[str]:
        result = self._request("GET", f"/api/v1/sessions/{session_id}/page-source")
        if result.get("success"):
            return result.get("data", {}).get("page_source")
        return None
