"""
services/candidate_service.py
Responsibility: All business logic for creating, reading, updating,
deactivating, and searching candidates.
"""

import datetime

from data.store import DataStore

MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75
REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Doctorate",
]


class CandidateService:
    """Manages candidate lifecycle — validation and CRUD operations."""

    def __init__(self, store: DataStore, audit_log_fn):
        self._store        = store
        self._log_action   = audit_log_fn  # callable(action, user, details)

    # ── Validation ───────────────────────────────────────────────────────────

    def validate_candidate(
        self,
        full_name:       str,
        national_id:     str,
        dob_str:         str,
        criminal_record: str,
    ):
        """Returns (age, None) on pass, or (None, error_message) on fail."""
        if not full_name:
            return None, "Name cannot be empty."
        if not national_id:
            return None, "National ID cannot be empty."
        if any(c["national_id"] == national_id for c in self._store.candidates.values()):
            return None, "A candidate with this National ID already exists."
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            return None, "Invalid date format. Use YYYY-MM-DD."
        if age < MIN_CANDIDATE_AGE:
            return None, f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}"
        if age > MAX_CANDIDATE_AGE:
            return None, f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}"
        if criminal_record == "yes":
            return None, "REJECTED:Candidates with criminal records are not eligible."
        return age, None

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def create_candidate(
        self,
        full_name:        str,
        national_id:      str,
        dob_str:          str,
        age:              int,
        gender:           str,
        education:        str,
        party:            str,
        manifesto:        str,
        address:          str,
        phone:            str,
        email:            str,
        years_experience: int,
        created_by:       str,
    ) -> int:
        """Creates the candidate and returns the new candidate ID."""
        cid = self._store.candidate_id_counter
        self._store.candidates[cid] = {
            "id":               cid,
            "full_name":        full_name,
            "national_id":      national_id,
            "date_of_birth":    dob_str,
            "age":              age,
            "gender":           gender,
            "education":        education,
            "party":            party,
            "manifesto":        manifesto,
            "address":          address,
            "phone":            phone,
            "email":            email,
            "has_criminal_record": False,
            "years_experience": years_experience,
            "is_active":        True,
            "is_approved":      True,
            "created_at":       str(datetime.datetime.now()),
            "created_by":       created_by,
        }
        self._log_action("CREATE_CANDIDATE", created_by, f"Created candidate: {full_name} (ID: {cid})")
        self._store.candidate_id_counter += 1
        self._store.save()
        return cid

    def get_all_candidates(self) -> dict:
        return self._store.candidates

    def get_candidate_by_id(self, cid: int):
        return self._store.candidates.get(cid)

    def update_candidate(self, cid: int, updates: dict, updated_by: str):
        """
        Applies only the non-empty values from `updates` to the candidate.
        updates keys: full_name, party, manifesto, phone, email, address, years_experience
        """
        c = self._store.candidates[cid]
        for field in ("full_name", "party", "manifesto", "phone", "email", "address"):
            if updates.get(field):
                c[field] = updates[field]
        if updates.get("years_experience") is not None:
            c["years_experience"] = updates["years_experience"]
        self._log_action("UPDATE_CANDIDATE", updated_by, f"Updated candidate: {c['full_name']} (ID: {cid})")
        self._store.save()

    def deactivate_candidate(self, cid: int, deleted_by: str):
        """Soft-delete: marks candidate as inactive."""
        # Guard: cannot deactivate if in an open poll
        for poll in self._store.polls.values():
            if poll["status"] == "open":
                for pos in poll.get("positions", []):
                    if cid in pos.get("candidate_ids", []):
                        return False, f"Cannot delete — candidate is in active poll: {poll['title']}"
        name = self._store.candidates[cid]["full_name"]
        self._store.candidates[cid]["is_active"] = False
        self._log_action("DELETE_CANDIDATE", deleted_by, f"Deactivated candidate: {name} (ID: {cid})")
        self._store.save()
        return True, name

    # ── Search ───────────────────────────────────────────────────────────────

    def search_by_name(self, term: str) -> list:
        return [c for c in self._store.candidates.values() if term.lower() in c["full_name"].lower()]

    def search_by_party(self, term: str) -> list:
        return [c for c in self._store.candidates.values() if term.lower() in c["party"].lower()]

    def search_by_education(self, education: str) -> list:
        return [c for c in self._store.candidates.values() if c["education"] == education]

    def search_by_age_range(self, min_age: int, max_age: int) -> list:
        return [c for c in self._store.candidates.values() if min_age <= c["age"] <= max_age]
