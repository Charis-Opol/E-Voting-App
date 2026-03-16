# models/store.py  ─  In-memory data store (single source of truth)
#
# One responsibility: hold all application state and expose typed accessors.
# No business logic lives here.

import datetime
import hashlib
import json
import os

from constants import DATA_FILE


class DataStore:
    """Holds all in-memory application state.  No business logic."""

    def __init__(self):
        self.candidates:          dict[int, dict] = {}
        self.candidate_id_counter: int = 1

        self.voting_stations:     dict[int, dict] = {}
        self.station_id_counter:  int = 1

        self.polls:               dict[int, dict] = {}
        self.poll_id_counter:     int = 1

        self.positions:           dict[int, dict] = {}
        self.position_id_counter: int = 1

        self.voters:              dict[int, dict] = {}
        self.voter_id_counter:    int = 1

        self.admins:              dict[int, dict] = {}
        self.admin_id_counter:    int = 1

        self.votes:               list[dict] = []
        self.audit_log:           list[dict] = []

        self._seed_default_admin()

    # ── seeding ───────────────────────────────────────────────────────────────

    def _seed_default_admin(self) -> None:
        self.admins[1] = {
            "id": 1,
            "username": "admin",
            "password": hashlib.sha256("admin123".encode()).hexdigest(),
            "full_name": "System Administrator",
            "email": "admin@evote.com",
            "role": "super_admin",
            "created_at": str(datetime.datetime.now()),
            "is_active": True,
        }
        self.admin_id_counter = 2

    # ── persistence ───────────────────────────────────────────────────────────

    def save(self) -> None:
        data = {
            "candidates":           self.candidates,
            "candidate_id_counter": self.candidate_id_counter,
            "voting_stations":      self.voting_stations,
            "station_id_counter":   self.station_id_counter,
            "polls":                self.polls,
            "poll_id_counter":      self.poll_id_counter,
            "positions":            self.positions,
            "position_id_counter":  self.position_id_counter,
            "voters":               self.voters,
            "voter_id_counter":     self.voter_id_counter,
            "admins":               self.admins,
            "admin_id_counter":     self.admin_id_counter,
            "votes":                self.votes,
            "audit_log":            self.audit_log,
        }
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"  Error saving data: {e}")

    def load(self) -> None:
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            self.candidates           = {int(k): v for k, v in data.get("candidates", {}).items()}
            self.candidate_id_counter = data.get("candidate_id_counter", 1)
            self.voting_stations      = {int(k): v for k, v in data.get("voting_stations", {}).items()}
            self.station_id_counter   = data.get("station_id_counter", 1)
            self.polls                = {int(k): v for k, v in data.get("polls", {}).items()}
            self.poll_id_counter      = data.get("poll_id_counter", 1)
            self.positions            = {int(k): v for k, v in data.get("positions", {}).items()}
            self.position_id_counter  = data.get("position_id_counter", 1)
            self.voters               = {int(k): v for k, v in data.get("voters", {}).items()}
            self.voter_id_counter     = data.get("voter_id_counter", 1)
            self.admins               = {int(k): v for k, v in data.get("admins", {}).items()}
            self.admin_id_counter     = data.get("admin_id_counter", 1)
            self.votes                = data.get("votes", [])
            self.audit_log            = data.get("audit_log", [])
        except Exception as e:
            print(f"  Error loading data: {e}")


# ── module-level singleton shared by all services and UI ──────────────────────
store = DataStore()
