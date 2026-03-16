"""
data/store.py
Responsibility: Holds all in-memory data and handles JSON persistence.
One class, one responsibility: own the data and load/save it.
"""

import json
import os
import datetime
import hashlib

from ui.console import print_info, print_error

DATA_FILE = "evoting_data.json"


class DataStore:
    """
    Central data store. All service classes receive a reference to this
    instance — they never keep their own copies of the data dicts.
    """

    def __init__(self):
        self.candidates:          dict = {}
        self.candidate_id_counter: int  = 1

        self.voting_stations:     dict = {}
        self.station_id_counter:  int  = 1

        self.polls:               dict = {}
        self.poll_id_counter:     int  = 1

        self.positions:           dict = {}
        self.position_id_counter: int  = 1

        self.voters:              dict = {}
        self.voter_id_counter:    int  = 1

        self.admins:              dict = {}
        self.admin_id_counter:    int  = 1

        self.votes:               list = []
        self.audit_log:           list = []

        self._seed_default_admin()

    # ── Seeding ──────────────────────────────────────────────────────────────

    def _seed_default_admin(self):
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

    # ── Persistence ──────────────────────────────────────────────────────────

    def save(self):
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
            print_info("Data saved successfully")
        except Exception as exc:
            print_error(f"Error saving data: {exc}")

    def load(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)

            def _int_keys(d):
                return {int(k): v for k, v in d.items()}

            self.candidates           = _int_keys(data.get("candidates", {}))
            self.candidate_id_counter = data.get("candidate_id_counter", 1)
            self.voting_stations      = _int_keys(data.get("voting_stations", {}))
            self.station_id_counter   = data.get("station_id_counter", 1)
            self.polls                = _int_keys(data.get("polls", {}))
            self.poll_id_counter      = data.get("poll_id_counter", 1)
            self.positions            = _int_keys(data.get("positions", {}))
            self.position_id_counter  = data.get("position_id_counter", 1)
            self.voters               = _int_keys(data.get("voters", {}))
            self.voter_id_counter     = data.get("voter_id_counter", 1)
            self.admins               = _int_keys(data.get("admins", {}))
            self.admin_id_counter     = data.get("admin_id_counter", 1)
            self.votes                = data.get("votes", [])
            self.audit_log            = data.get("audit_log", [])

            print_info("Data loaded successfully")
        except Exception as exc:
            print_error(f"Error loading data: {exc}")
