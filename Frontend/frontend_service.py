"""
frontend_service.py

Abstraction layer that exposes cleanly named methods for the frontend UI.
This removes raw data manipulation and direct iterations over data structures
from the UI layer (SRP, Dependency Inversion).
"""
import datetime
import random
import string

from security import hash_password
from Backend.voters_management import GetAllVoters, VoterStore
from Backend.station_management import GetAllStations
from Backend.audits import LogAuditEntry

class AuthenticateVoter:
    """Authenticates a voter using card number and plain text password."""
    
    def execute(self, voter_card_number: str, plain_password: str) -> dict:
        voters = GetAllVoters().execute()
        hashed = hash_password(plain_password)
        
        for voter in voters:
            if voter["voter_card_number"] == voter_card_number and voter["password"] == hashed:
                if not voter["is_active"]:
                    raise PermissionError("This voter account has been deactivated.")
                if not voter["is_verified"]:
                    raise PermissionError("Your voter registration has not been verified yet.\nPlease contact an admin to verify your registration.")
                return voter
                
        raise ValueError("Invalid voter card number or password.")


class RegisterVoterProcess:
    """Registers a new voter after validating rules."""
    
    def execute(self, full_name, national_id, dob_str, gender, address, phone, email, plain_password, station_id, min_age=18) -> dict:
        voters = GetAllVoters().execute()
        for v in voters:
            if v["national_id"] == national_id:
                raise ValueError("A voter with this National ID already exists.")
                
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Expected YYYY-MM-DD.")
            
        age = (datetime.datetime.now() - dob).days // 365
        if age < min_age:
            raise ValueError(f"You must be at least {min_age} years old to register.")
            
        if len(plain_password) < 6:
            raise ValueError("Password must be at least 6 characters.")
            
        stations = GetAllStations().execute()
        selected_station = next((st for st in stations if st["id"] == station_id), None)
        if not selected_station or not selected_station["is_active"]:
            raise ValueError("Invalid station selection.")
            
        voter_card = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        
        voter_record = {
            "full_name": full_name, "national_id": national_id,
            "date_of_birth": dob_str, "age": age, "gender": gender, "address": address,
            "phone": phone, "email": email, "password": hash_password(plain_password),
            "voter_card_number": voter_card, "station_id": station_id,
            "is_verified": False, "is_active": True, "has_voted_in": [],
            "registered_at": str(datetime.datetime.now()), "role": "voter",
        }
        
        VoterStore.get().insert(voter_record)
        return voter_record


class GetAllCandidatesService:
    """Fetches candidates from the backend candidate_management DataStore."""
    def execute(self) -> list[dict]:
        from Backend.candidate_management import DataStore
        return list(DataStore.candidates.values())


class GetAllVotesService:
    """Fetches votes from the backend storage."""
    def execute(self) -> list[dict]:
        from Backend.storage import JsonStore
        return JsonStore("data/votes.json").all()


class CastVoteProcess:
    """Records votes and updates voter state and poll state."""
    
    def execute(self, current_user: dict, poll_id: int, my_votes: list, vote_hash: str, vote_timestamp: str) -> None:
        from Backend.storage import JsonStore
        from Backend.voters_management import UpdateVoter
        from Backend.polls_management import GetAllPolls, UpdatePoll
        from Backend.audits import LogAuditEntry
        
        votes_store = JsonStore("data/votes.json")
        for mv in my_votes:
            votes_store.insert({
                "vote_id": vote_hash + str(mv["position_id"]),
                "poll_id": poll_id,
                "position_id": mv["position_id"],
                "candidate_id": mv["candidate_id"],
                "voter_id": current_user["id"],
                "station_id": current_user["station_id"],
                "timestamp": vote_timestamp,
                "abstained": mv["abstained"]
            })
            
        current_user["has_voted_in"].append(poll_id)
        UpdateVoter().execute(current_user["id"], {"has_voted_in": current_user.get("has_voted_in", [])})
        
        # update total count
        polls = {p["id"]: p for p in GetAllPolls().execute()}
        if poll_id in polls:
            UpdatePoll().execute(poll_id, {"total_votes_cast": polls[poll_id]["total_votes_cast"] + 1})
            
        LogAuditEntry().execute(
            "CAST_VOTE", 
            current_user["voter_card_number"], 
            f"Voted in poll: {polls[poll_id]['title']} (Hash: {vote_hash})"
        )


