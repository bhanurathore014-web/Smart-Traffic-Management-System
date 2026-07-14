import requests
import urllib.parse
from typing import Dict, Any, List, Optional

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = urllib.parse.urljoin(f"{self.base_url}/", endpoint.lstrip("/"))
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, json: Dict[str, Any]) -> Any:
        url = urllib.parse.urljoin(f"{self.base_url}/", endpoint.lstrip("/"))
        response = requests.post(url, json=json)
        response.raise_for_status()
        return response.json()

    def _patch(self, endpoint: str, json: Dict[str, Any]) -> Any:
        url = urllib.parse.urljoin(f"{self.base_url}/", endpoint.lstrip("/"))
        response = requests.patch(url, json=json)
        response.raise_for_status()
        return response.json()

    # Cameras
    def get_cameras(self) -> List[Dict[str, Any]]:
        return self._get("cameras/")

    def get_active_cameras(self) -> List[Dict[str, Any]]:
        return self._get("cameras/active")

    # Traffic
    def get_recent_traffic(self, camera_id: str) -> List[Dict[str, Any]]:
        return self._get(f"traffic/{camera_id}/recent")

    # Signals
    def get_last_signal(self, camera_id: str) -> Dict[str, Any]:
        return self._get(f"signals/{camera_id}/last")
        
    # Emergencies
    def get_active_emergencies(self) -> List[Dict[str, Any]]:
        return self._get("emergencies/active")
        
    def resolve_emergency(self, emergency_id: str, notes: str = "Resolved via Dashboard") -> Dict[str, Any]:
        return self._post(f"emergencies/{emergency_id}/resolve", json={"notes": notes})
        
    # Analytics
    def get_analytics_trend(self, camera_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        return self._get(f"analytics/{camera_id}/trend", params={"hours": hours})
