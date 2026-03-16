"""
services/auth_service.py
Responsibility: Authentication logic — login validation, voter registration, password hashing,
voter card generation, audit logging.
"""

import datetime
import hashlib
import random
import string
from data.store import DataStore
from ui.console import Console  

console = Console()

MIN_VOTER_AGE = 18

class AuthService:
    """Handles all authentication and registration business logic."""

    def __init__(self, store: DataStore):
        self._store = store

    # ── Utilities ────────────────────────────────────────────────────────────
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_voter_card_number(self) -> str:
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

    def log_action(self, action: str, user: str, details: str):
        self._store.audit_log.append({
            "timestamp": str(datetime.datetime.now()),
            "action": action,
            "user": user,
            "details": details,
        })

    # ── Admin login ──────────────────────────────────────────────────────────
    def authenticate_admin(self, username: str, password: str):
        hashed = self.hash_password(password)
        for admin in self._store.admins.values():
            if admin["username"] == username and admin["password"] == hashed:
                if not admin["is_active"]:
                    self.log_action("LOGIN_FAILED", username, "Account deactivated")
                    return None, "This account has been deactivated."
                self.log_action("LOGIN", username, "Admin login successful")
                return admin, None
        self.log_action("LOGIN_FAILED", username, "Invalid admin credentials")
        return None, "Invalid credentials."

    # ── Voter login ──────────────────────────────────────────────────────────
    def authenticate_voter(self, voter_card: str, password: str):
        hashed = self.hash_password(password)
        for voter in self._store.voters.values():
            if voter["voter_card_number"] == voter_card and voter["password"] == hashed:
                if not voter["is_active"]:
                    self.log_action("LOGIN_FAILED", voter_card, "Voter account deactivated")
                    return None, "This voter account has been deactivated."
                if not voter["is_verified"]:
                    self.log_action("LOGIN_FAILED", voter_card, "Voter not verified")
                    return None, "WARNING:Your voter registration has not been verified yet. Please contact an admin."
                self.log_action("LOGIN", voter_card, "Voter login successful")
                return voter, None
        self.log_action("LOGIN_FAILED", voter_card, "Invalid voter credentials")
        return None, "Invalid voter card number or password."

    # ── Registration / validation ────────────────────────────────────────────
    def validate_voter_registration(
        self, full_name, national_id, dob_str, gender, password, confirm_password, station_id
    ):
        if not full_name:
            return False, "Name cannot be empty."
        if not national_id:
            return False, "National ID cannot be empty."
        if any(v["national_id"] == national_id for v in self._store.voters.values()):
            return False, "A voter with this National ID already exists."
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
            if age < MIN_VOTER_AGE:
                return False, f"You must be at least {MIN_VOTER_AGE} years old to register."
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD."
        if gender not in ("M", "F", "OTHER"):
            return False, "Invalid gender selection."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        if password != confirm_password:
            return False, "Passwords do not match."
        if not self._store.voting_stations:
            return False, "No voting stations available. Contact admin."
        if station_id not in self._store.voting_stations or not self._store.voting_stations[station_id]["is_active"]:
            return False, "Invalid station selection."
        return True, None

    def register_voter(
        self, full_name, national_id, dob_str, age, gender, address, phone, email, password, station_id
    ) -> str:
        voter_card = self.generate_voter_card_number()
        vid = self._store.voter_id_counter
        self._store.voters[vid] = {
            "id": vid,
            "full_name": full_name,
            "national_id": national_id,
            "date_of_birth": dob_str,
            "age": age,
            "gender": gender,
            "address": address,
            "phone": phone,
            "email": email,
            "password": self.hash_password(password),
            "voter_card_number": voter_card,
            "station_id": station_id,
            "is_verified": False,
            "is_active": True,
            "has_voted_in": [],
            "registered_at": str(datetime.datetime.now()),
            "role": "voter",
        }
        self.log_action("REGISTER", full_name, f"New voter registered with card: {voter_card}")
        self._store.voter_id_counter += 1
        self._store.save()
        return voter_card

    # ── Password change ──────────────────────────────────────────────────────
    def change_voter_password(self, voter, old_password, new_password, confirm_password):
        if self.hash_password(old_password) != voter["password"]:
            return False, "Incorrect current password."
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters."
        if new_password != confirm_password:
            return False, "Passwords do not match."
        new_hashed = self.hash_password(new_password)
        voter["password"] = new_hashed
        for v in self._store.voters.values():
            if v["id"] == voter["id"]:
                v["password"] = new_hashed
                break
        self.log_action("CHANGE_PASSWORD", voter["voter_card_number"], "Password changed")
        self._store.save()
        return True, None

    def logout_admin(self, admin):
        self.log_action("LOGOUT", admin["username"], "Admin logged out")
        self._store.save()

    def logout_voter(self, voter):
        self.log_action("LOGOUT", voter["voter_card_number"], "Voter logged out")
        self._store.save()