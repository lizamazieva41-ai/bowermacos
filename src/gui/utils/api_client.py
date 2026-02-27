"""
GUI API Client - Handles communication with the backend API
"""

import json
from typing import Optional, Dict, Any, List
import urllib.request
import urllib.error


class GUIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None

    def set_token(self, token: str):
        self.token = token

    def clear_token(self):
        self.token = None

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        req_data = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode("utf-8")
                return json.loads(content) if content else {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                error_data = json.loads(error_body)
                raise Exception(error_data.get("detail", str(e)))
            except:
                raise Exception(f"HTTP {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"Connection failed: {e.reason}")

    def get(self, endpoint: str) -> Dict[str, Any]:
        return self._request("GET", endpoint)

    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request("POST", endpoint, data)

    def put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request("PUT", endpoint, data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        return self._request("DELETE", endpoint)

    def login(self, username: str, password: str) -> Dict[str, Any]:
        result = self.post("/api/v1/auth/login", {"username": username, "password": password})
        if result.get("success"):
            token = result.get("data", {}).get("access_token")
            if token:
                self.set_token(token)
        return result

    def login_with_api_key(self, api_key: str) -> bool:
        self.set_token(api_key)
        try:
            self.get("/api/v1/profiles")
            return True
        except:
            self.clear_token()
            return False

    def get_profiles(self) -> List[Dict]:
        result = self.get("/api/v1/profiles")
        if result.get("success"):
            return result.get("data", {}).get("profiles", [])
        return []

    def create_profile(self, profile_data: Dict) -> Dict:
        return self.post("/api/v1/profiles", profile_data)

    def update_profile(self, profile_id: int, profile_data: Dict) -> Dict:
        return self.put(f"/api/v1/profiles/{profile_id}", profile_data)

    def delete_profile(self, profile_id: int) -> Dict:
        return self.delete(f"/api/v1/profiles/{profile_id}")

    def clone_profile(self, profile_id: int, new_name: str) -> Dict:
        return self.post(f"/api/v1/profiles/{profile_id}/clone", {"name": new_name})

    def get_sessions(self) -> List[Dict]:
        return self.get("/api/v1/sessions")

    def create_session(self, profile_id: int) -> Dict:
        return self.post(f"/api/v1/sessions?profile_id={profile_id}", {})

    def close_session(self, session_id: str) -> Dict:
        return self.delete(f"/api/v1/sessions/{session_id}")

    def get_proxies(self) -> List[Dict]:
        result = self.get("/api/v1/proxies")
        if result.get("success"):
            return result.get("data", {}).get("proxies", [])
        return []

    def create_proxy(self, proxy_data: Dict) -> Dict:
        return self.post("/api/v1/proxies", proxy_data)

    def update_proxy(self, proxy_id: int, proxy_data: Dict) -> Dict:
        return self.put(f"/api/v1/proxies/{proxy_id}", proxy_data)

    def delete_proxy(self, proxy_id: int) -> Dict:
        return self.delete(f"/api/v1/proxies/{proxy_id}")

    def test_proxy(self, proxy_id: int) -> Dict:
        return self.post(f"/api/v1/proxies/{proxy_id}/test", {})

    def get_metrics(self) -> Dict:
        return self.get("/api/v1/metrics")

    def get_health(self) -> Dict:
        return self.get("/health")

    def close(self):
        pass
