"""
services/station_service.py
Responsibility: Business logic for voting station CRUD.
"""

import datetime
from data.store import DataStore


class StationService:

    def __init__(self, store: DataStore, audit_log_fn):
        self._store      = store
        self._log_action = audit_log_fn

    def create_station(self, name, location, region, capacity, supervisor, contact,
                       opening_time, closing_time, created_by) -> int:
        sid = self._store.station_id_counter
        self._store.voting_stations[sid] = {
            "id":            sid,
            "name":          name,
            "location":      location,
            "region":        region,
            "capacity":      capacity,
            "registered_voters": 0,
            "supervisor":    supervisor,
            "contact":       contact,
            "opening_time":  opening_time,
            "closing_time":  closing_time,
            "is_active":     True,
            "created_at":    str(datetime.datetime.now()),
            "created_by":    created_by,
        }
        self._log_action("CREATE_STATION", created_by, f"Created station: {name} (ID: {sid})")
        self._store.station_id_counter += 1
        self._store.save()
        return sid

    def get_all_stations(self) -> dict:
        return self._store.voting_stations

    def get_station_by_id(self, sid: int):
        return self._store.voting_stations.get(sid)

    def get_registered_voter_count(self, sid: int) -> int:
        return sum(1 for v in self._store.voters.values() if v["station_id"] == sid)

    def update_station(self, sid: int, updates: dict, updated_by: str):
        s = self._store.voting_stations[sid]
        for field in ("name", "location", "region", "supervisor", "contact"):
            if updates.get(field):
                s[field] = updates[field]
        if updates.get("capacity") is not None:
            s["capacity"] = updates["capacity"]
        self._log_action("UPDATE_STATION", updated_by, f"Updated station: {s['name']} (ID: {sid})")
        self._store.save()

    def deactivate_station(self, sid: int, deleted_by: str) -> tuple:
        voter_count = self.get_registered_voter_count(sid)
        name = self._store.voting_stations[sid]["name"]
        self._store.voting_stations[sid]["is_active"] = False
        self._log_action("DELETE_STATION", deleted_by, f"Deactivated station: {name}")
        self._store.save()
        return voter_count, name
