import json
import os
from typing import Dict, List, Optional
from app.schemas import InspectionResponse


STORAGE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "inspections.json"
)


class StorageService:
    def __init__(self):
        self._inspections: Dict[str, Dict] = {}
        self._ensure_storage_dir()
        self._load_from_disk()

    def _ensure_storage_dir(self):
        dir_path = os.path.dirname(STORAGE_FILE)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

    def _load_from_disk(self):
        if os.path.exists(STORAGE_FILE):
            try:
                with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                    self._inspections = json.load(f)
            except Exception as e:
                print(f"Failed to load inspections from storage: {e}")
                self._inspections = {}

    def _save_to_disk(self):
        try:
            with open(STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._inspections, f, indent=2)
        except Exception as e:
            print(f"Failed to save inspections to disk: {e}")

    def save_inspection(self, inspection: InspectionResponse):
        data = inspection.model_dump()
        self._inspections[inspection.inspection_id] = data
        self._save_to_disk()

    def get_inspection(self, inspection_id: str) -> Optional[Dict]:
        return self._inspections.get(inspection_id)

    def get_all_inspections(self) -> List[Dict]:
        # Return sorted by timestamp descending
        items = list(self._inspections.values())
        items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return items

    def get_stats(self) -> Dict[str, int]:
        total = len(self._inspections)
        compliant = sum(1 for i in self._inspections.values() if i.get("status") == "COMPLIANT")
        non_compliant = sum(
            1 for i in self._inspections.values() if i.get("status") == "NON_COMPLIANT"
        )
        needs_review = sum(
            1 for i in self._inspections.values() if i.get("status") == "NEEDS_REVIEW"
        )
        return {
            "total": total,
            "compliant": compliant,
            "non_compliant": non_compliant,
            "needs_review": needs_review,
        }


storage_service = StorageService()
