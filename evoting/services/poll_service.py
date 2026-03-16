"""
services/poll_service.py
Responsibility: Business logic for poll/election CRUD, open/close, and
candidate assignment.
"""

import datetime
from data.store import DataStore

MIN_CANDIDATE_AGE = 25


class PollService:

    def __init__(self, store: DataStore, audit_log_fn):
        self._store      = store
        self._log_action = audit_log_fn

    def create_poll(self, title, description, election_type,
                    start_date, end_date, poll_positions,
                    selected_station_ids, created_by) -> int:
        pid = self._store.poll_id_counter
        self._store.polls[pid] = {
            "id":              pid,
            "title":           title,
            "description":     description,
            "election_type":   election_type,
            "start_date":      start_date,
            "end_date":        end_date,
            "positions":       poll_positions,
            "station_ids":     selected_station_ids,
            "status":          "draft",
            "total_votes_cast": 0,
            "created_at":      str(datetime.datetime.now()),
            "created_by":      created_by,
        }
        self._log_action("CREATE_POLL", created_by, f"Created poll: {title} (ID: {pid})")
        self._store.poll_id_counter += 1
        self._store.save()
        return pid

    def get_all_polls(self) -> dict:
        return self._store.polls

    def get_poll_by_id(self, pid: int):
        return self._store.polls.get(pid)

    def update_poll(self, pid: int, updates: dict, updated_by: str) -> tuple:
        """Returns (True, None) or (False, error_message)."""
        poll = self._store.polls[pid]
        if poll["status"] == "open":
            return False, "Cannot update an open poll. Close it first."
        if poll["status"] == "closed" and poll["total_votes_cast"] > 0:
            return False, "Cannot update a poll with votes."
        if updates.get("title"):
            poll["title"] = updates["title"]
        if updates.get("description"):
            poll["description"] = updates["description"]
        if updates.get("election_type"):
            poll["election_type"] = updates["election_type"]
        if updates.get("start_date"):
            poll["start_date"] = updates["start_date"]
        if updates.get("end_date"):
            poll["end_date"] = updates["end_date"]
        self._log_action("UPDATE_POLL", updated_by, f"Updated poll: {poll['title']}")
        self._store.save()
        return True, None

    def delete_poll(self, pid: int, deleted_by: str) -> tuple:
        """Returns (True, title) or (False, error_message)."""
        poll = self._store.polls[pid]
        if poll["status"] == "open":
            return False, "Cannot delete an open poll. Close it first."
        title = poll["title"]
        vote_count = poll["total_votes_cast"]
        del self._store.polls[pid]
        self._store.votes = [v for v in self._store.votes if v["poll_id"] != pid]
        self._log_action("DELETE_POLL", deleted_by, f"Deleted poll: {title}")
        self._store.save()
        return True, (title, vote_count)

    def set_poll_status(self, pid: int, new_status: str, changed_by: str) -> tuple:
        """
        Opens, closes, or reopens a poll.
        Returns (True, message) or (False, error_message).
        """
        poll = self._store.polls[pid]
        if new_status == "open":
            if poll["status"] == "draft":
                if not any(pos["candidate_ids"] for pos in poll["positions"]):
                    return False, "Cannot open — no candidates assigned."
            poll["status"] = "open"
            action = "OPEN_POLL" if poll["status"] != "closed" else "REOPEN_POLL"
            self._log_action(action, changed_by, f"Opened poll: {poll['title']}")
            self._store.save()
            return True, f"Poll '{poll['title']}' is now OPEN for voting!"
        elif new_status == "closed":
            poll["status"] = "closed"
            self._log_action("CLOSE_POLL", changed_by, f"Closed poll: {poll['title']}")
            self._store.save()
            return True, f"Poll '{poll['title']}' is now CLOSED."
        return False, "Unknown status."

    def assign_candidates(self, pid: int, position_index: int,
                          candidate_ids: list, assigned_by: str) -> tuple:
        """
        Sets the candidate list for a specific position within a poll.
        Returns (valid_ids_count, skipped_names).
        """
        poll = self._store.polls[pid]
        pos  = poll["positions"][position_index]
        pos_data    = self._store.positions.get(pos["position_id"], {})
        min_age     = pos_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
        eligible    = {
            cid: c for cid, c in self._store.candidates.items()
            if c["is_active"] and c["is_approved"] and c["age"] >= min_age
        }
        valid_ids = []
        skipped   = []
        for cid in candidate_ids:
            if cid in eligible:
                valid_ids.append(cid)
            else:
                skipped.append(str(cid))
        pos["candidate_ids"] = valid_ids
        self._log_action("ASSIGN_CANDIDATES", assigned_by, f"Updated candidates for poll: {poll['title']}")
        self._store.save()
        return len(valid_ids), skipped

    # ── Result helpers ───────────────────────────────────────────────────────

    def calculate_position_results(self, pid: int, position_id: int) -> dict:
        """
        Returns {
          'vote_counts':    {candidate_id: count},
          'abstain_count':  int,
          'total_pos':      int,
        }
        """
        vote_counts   = {}
        abstain_count = 0
        total_pos     = 0
        for v in self._store.votes:
            if v["poll_id"] == pid and v["position_id"] == position_id:
                total_pos += 1
                if v["abstained"]:
                    abstain_count += 1
                else:
                    vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
        return {"vote_counts": vote_counts, "abstain_count": abstain_count, "total_pos": total_pos}

    def calculate_turnout(self, pid: int) -> tuple:
        """Returns (total_eligible, turnout_percentage)."""
        poll = self._store.polls[pid]
        total_eligible = sum(
            1 for v in self._store.voters.values()
            if v["is_verified"] and v["is_active"] and v["station_id"] in poll["station_ids"]
        )
        turnout = (poll["total_votes_cast"] / total_eligible * 100) if total_eligible > 0 else 0
        return total_eligible, turnout

    def calculate_station_results(self, pid: int, sid: int) -> dict:
        """Returns per-station vote tallies for a poll."""
        station_votes = [v for v in self._store.votes if v["poll_id"] == pid and v["station_id"] == sid]
        voted_count   = len(set(v["voter_id"] for v in station_votes))
        registered    = sum(
            1 for v in self._store.voters.values()
            if v["station_id"] == sid and v["is_verified"] and v["is_active"]
        )
        turnout = (voted_count / registered * 100) if registered > 0 else 0
        return {
            "station_votes": station_votes,
            "voted_count":   voted_count,
            "registered":    registered,
            "turnout":       turnout,
        }
    def get_poll_results(self, pid: int) -> dict:
        """Aggregates votes by candidate name for the given poll ID."""
        counts = {}
        target_poll = self._store.polls.get(pid)
        if not target_poll:
            return {}

        for v in self._store.votes:
            if v["poll_id"] == pid and not v["abstained"]:
                cid = v["candidate_id"]
                candidate = self._store.candidates.get(cid, {})
                name = candidate.get("full_name", f"Unknown Candidate (ID: {cid})")
                counts[name] = counts.get(name, 0) + 1
        
        return counts
