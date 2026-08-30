"""Inspection Storage Service: local JSON / in-memory persistence abstraction."""
import os
import json
import logging
from typing import List, Optional, Dict
from datetime import datetime
from ..schemas import InspectionResponse

logger = logging.getLogger(__name__)

STORAGE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "inspections_store.json")


class StorageService:
    """Manages inspection history with local JSON persistence and memory cache."""

    def __init__(self, file_path: str = STORAGE_FILE):
        self.file_path = file_path
        self._cache: Dict[str, dict] = {}
        self._ensure_storage_dir()
        self._load_from_disk()

    def _ensure_storage_dir(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def _load_from_disk(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._cache = {item["inspection_id"]: item for item in data if "inspection_id" in item}
                    elif isinstance(data, dict):
                        self._cache = data
            except Exception as e:
                logger.warning(f"Could not load inspections from disk: {e}")
                self._cache = {}

    def _save_to_disk(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(list(self._cache.values()), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to persist inspections to disk: {e}")

    def save(self, inspection: InspectionResponse) -> InspectionResponse:
        data = inspection.model_dump()
        self._cache[inspection.inspection_id] = data
        self._save_to_disk()
        return inspection

    def get(self, inspection_id: str) -> Optional[InspectionResponse]:
        item = self._cache.get(inspection_id)
        if item:
            try:
                return InspectionResponse(**item)
            except Exception as e:
                logger.error(f"Error deserializing inspection {inspection_id}: {e}")
                return None
        return None

    def list_all(self) -> List[dict]:
        """Return all inspections sorted descending by creation timestamp."""
        items = list(self._cache.values())
        # Sort by created_at desc if available
        return sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)

    def clear(self):
        self._cache.clear()
        self._save_to_disk()


storage_service = StorageService()
