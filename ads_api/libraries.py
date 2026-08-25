from typing import Any, Dict, List, Optional, Union
from ads_api.client import ADSClient

class LibraryService:
    """
    Service for managing ADS personal and collaborative Libraries (biblib).
    """
    def __init__(self, client: Optional[ADSClient] = None):
        self.client = client or ADSClient()

    def list_libraries(self, start: int = 0, rows: int = 20, sort: str = "date_created", order: str = "asc") -> List[Dict[str, Any]]:
        """
        List all libraries owned or accessible by the user.
        """
        params = {"start": start, "rows": rows, "sort": sort, "order": order}
        res = self.client.get("biblib/libraries", params=params)
        return res.json().get("libraries", [])

    def get_library(self, library_id: str, start: int = 0, rows: int = 100) -> Dict[str, Any]:
        """
        Retrieve details and documents of a specific library.
        """
        params = {"start": start, "rows": rows}
        res = self.client.get(f"biblib/libraries/{library_id}", params=params)
        return res.json()

    def create_library(
        self,
        name: str,
        description: str = "Created via ADS Python API",
        public: bool = False,
        bibcodes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new library.
        """
        payload: Dict[str, Any] = {
            "name": name,
            "description": description,
            "public": public,
            "bibcode": bibcodes or []
        }
        res = self.client.post("biblib/libraries", json_data=payload)
        return res.json()

    def add_documents(self, library_id: str, bibcodes: List[str]) -> Dict[str, Any]:
        """
        Add bibcodes to an existing library.
        """
        payload = {
            "action": "add",
            "bibcode": bibcodes
        }
        res = self.client.post(f"biblib/documents/{library_id}", json_data=payload)
        return res.json()

    def remove_documents(self, library_id: str, bibcodes: List[str]) -> Dict[str, Any]:
        """
        Remove bibcodes from an existing library.
        """
        payload = {
            "action": "remove",
            "bibcode": bibcodes
        }
        res = self.client.post(f"biblib/documents/{library_id}", json_data=payload)
        return res.json()

    def update_library_metadata(
        self,
        library_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        public: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update library metadata (name, description, public visibility).
        """
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if public is not None:
            payload["public"] = public
            
        res = self.client.put(f"biblib/documents/{library_id}", json_data=payload)
        return res.json()

    def delete_library(self, library_id: str) -> Dict[str, Any]:
        """
        Delete an entire library.
        """
        res = self.client.delete(f"biblib/documents/{library_id}")
        return res.json()

    def get_permissions(self, library_id: str) -> Dict[str, Any]:
        """
        View permissions for a library.
        """
        res = self.client.get(f"biblib/permissions/{library_id}")
        return res.json()

    def set_permission(self, library_id: str, email: str, permission: str = "read") -> Dict[str, Any]:
        """
        Set or update user permission for a library ('read', 'write', 'admin', 'owner').
        """
        payload = {"email": email, "permission": permission}
        res = self.client.post(f"biblib/permissions/{library_id}", json_data=payload)
        return res.json()
