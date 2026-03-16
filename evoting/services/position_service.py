"""
services/position_service.py
Responsibility: Business logic for election position CRUD.
"""

import datetime
from data.store import DataStore

MIN_CANDIDATE_AGE = 25


class PositionService:

    def __init__(self, store: DataStore, audit_log_fn):
        self._store      = store
        self._log_action = audit_log_fn

    def create_position(self, title, description, level, max_winners,
                        min_candidate_age, created_by) -> int:
        pid = self._store.position_id_counter
        self._store.positions[pid] = {
            "id":                pid,
            "title":             title,
            "description":       description,
            "level":             level.capitalize(),
            "max_winners":       max_winners,
            "min_candidate_age": min_candidate_age,
            "is_active":         True,
            "created_at":        str(datetime.datetime.now()),
            "created_by":        created_by,
        }
        self._log_action("CREATE_POSITION", created_by, f"Created position: {title} (ID: {pid})")
        self._store.position_id_counter += 1
        self._store.save()
        return pid

    def get_all_positions(self) -> dict:
        return self._store.positions

    def get_position_by_id(self, pid: int):
        return self._store.positions.get(pid)

    def update_position(self, pid: int, updates: dict, updated_by: str):
        p = self._store.positions[pid]
        if updates.get("title"):
            p["title"] = updates["title"]
        if updates.get("description"):
            p["description"] = updates["description"]
        if updates.get("level") and updates["level"].lower() in ("national", "regional", "local"):
            p["level"] = updates["level"].capitalize()
        if updates.get("max_winners") is not None:
            p["max_winners"] = updates["max_winners"]
        self._log_action("UPDATE_POSITION", updated_by, f"Updated position: {p['title']}")
        self._store.save()

    def deactivate_position(self, pid: int, deleted_by: str) -> tuple:
        """Returns (True, title) or (False, error_message)."""
        for poll in self._store.polls.values():
            for pp in poll.get("positions", []):
                if pp["position_id"] == pid and poll["status"] == "open":
                    return False, f"Cannot delete — in active poll: {poll['title']}"
        title = self._store.positions[pid]["title"]
        self._store.positions[pid]["is_active"] = False
        self._log_action("DELETE_POSITION", deleted_by, f"Deactivated position: {title}")
        self._store.save()
        return True, title
