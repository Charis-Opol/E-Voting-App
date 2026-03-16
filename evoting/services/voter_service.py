"""
services/voter_service.py
Responsibility: Admin-side voter management — view, verify, deactivate, search.
(Self-service voter actions live in auth_service and vote_service.)
"""

from data.store import DataStore


class VoterService:

    def __init__(self, store: DataStore, audit_log_fn):
        self._store      = store
        self._log_action = audit_log_fn

    def get_all_voters(self) -> dict:
        return self._store.voters

    def get_voter_by_id(self, vid: int):
        return self._store.voters.get(vid)

    def get_unverified_voters(self) -> dict:
        return {vid: v for vid, v in self._store.voters.items() if not v["is_verified"]}

    def verify_voter(self, vid: int, verified_by: str) -> tuple:
        """Returns (True, name) or (False, error_message)."""
        if vid not in self._store.voters:
            return False, "Voter not found."
        if self._store.voters[vid]["is_verified"]:
            return False, "Already verified."
        self._store.voters[vid]["is_verified"] = True
        name = self._store.voters[vid]["full_name"]
        self._log_action("VERIFY_VOTER", verified_by, f"Verified voter: {name}")
        self._store.save()
        return True, name

    def verify_all_pending(self, verified_by: str) -> int:
        unverified = self.get_unverified_voters()
        for vid in unverified:
            self._store.voters[vid]["is_verified"] = True
        count = len(unverified)
        self._log_action("VERIFY_ALL_VOTERS", verified_by, f"Verified {count} voters")
        self._store.save()
        return count

    def deactivate_voter(self, vid: int, deactivated_by: str) -> tuple:
        """Returns (True, name) or (False, error_message)."""
        if vid not in self._store.voters:
            return False, "Voter not found."
        if not self._store.voters[vid]["is_active"]:
            return False, "Already deactivated."
        self._store.voters[vid]["is_active"] = False
        name = self._store.voters[vid]["full_name"]
        self._log_action("DEACTIVATE_VOTER", deactivated_by, f"Deactivated voter: {name}")
        self._store.save()
        return True, name

    def search_by_name(self, term: str) -> list:
        return [v for v in self._store.voters.values() if term.lower() in v["full_name"].lower()]

    def search_by_card_number(self, card: str) -> list:
        return [v for v in self._store.voters.values() if v["voter_card_number"] == card]

    def search_by_national_id(self, nid: str) -> list:
        return [v for v in self._store.voters.values() if v["national_id"] == nid]

    def search_by_station(self, sid: int) -> list:
        return [v for v in self._store.voters.values() if v["station_id"] == sid]
