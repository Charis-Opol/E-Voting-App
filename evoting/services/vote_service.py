"""
services/vote_service.py
Responsibility: The actual voting process — casting votes and
retrieving a voter's history.
"""

import datetime
import hashlib

from data.store import DataStore


class VoteService:

    def __init__(self, store: DataStore, audit_log_fn):
        self._store      = store
        self._log_action = audit_log_fn

    def get_available_polls_for_voter(self, voter: dict) -> dict:
        """Returns polls that are open, belong to the voter's station,
        and that the voter has not yet voted in."""
        return {
            pid: p for pid, p in self._store.polls.items()
            if p["status"] == "open"
            and pid not in voter.get("has_voted_in", [])
            and voter["station_id"] in p["station_ids"]
        }

    def get_open_polls(self) -> dict:
        return {pid: p for pid, p in self._store.polls.items() if p["status"] == "open"}

    def get_closed_polls(self) -> dict:
        return {pid: p for pid, p in self._store.polls.items() if p["status"] == "closed"}

    def cast_votes(self, voter: dict, pid: int, vote_selections: list) -> str:
        """
        Commits votes and returns the vote reference hash.
        vote_selections: list of dicts with keys
            position_id, position_title, candidate_id (None if abstain), abstained (bool)
        """
        vote_timestamp = str(datetime.datetime.now())
        vote_hash = hashlib.sha256(
            f"{voter['id']}{pid}{vote_timestamp}".encode()
        ).hexdigest()[:16]

        for sel in vote_selections:
            self._store.votes.append({
                "vote_id":      vote_hash + str(sel["position_id"]),
                "poll_id":      pid,
                "position_id":  sel["position_id"],
                "candidate_id": sel.get("candidate_id"),
                "voter_id":     voter["id"],
                "station_id":   voter["station_id"],
                "timestamp":    vote_timestamp,
                "abstained":    sel["abstained"],
            })

        # Mark voter as having voted
        voter["has_voted_in"].append(pid)
        for v in self._store.voters.values():
            if v["id"] == voter["id"]:
                v["has_voted_in"].append(pid)
                break

        self._store.polls[pid]["total_votes_cast"] += 1
        self._log_action(
            "CAST_VOTE",
            voter["voter_card_number"],
            f"Voted in poll: {self._store.polls[pid]['title']} (Hash: {vote_hash})"
        )
        self._store.save()
        return vote_hash

    def get_voter_vote_records(self, voter_id: int, pid: int) -> list:
        return [v for v in self._store.votes if v["poll_id"] == pid and v["voter_id"] == voter_id]

    def get_statistics(self) -> dict:
        """Returns system-wide statistics for the admin stats screen."""
        s = self._store
        tc  = len(s.candidates)
        ac  = sum(1 for c in s.candidates.values() if c["is_active"])
        tv  = len(s.voters)
        vv  = sum(1 for v in s.voters.values() if v["is_verified"])
        av  = sum(1 for v in s.voters.values() if v["is_active"])
        tst = len(s.voting_stations)
        ast = sum(1 for st in s.voting_stations.values() if st["is_active"])
        tp  = len(s.polls)
        op  = sum(1 for p in s.polls.values() if p["status"] == "open")
        cp  = sum(1 for p in s.polls.values() if p["status"] == "closed")
        dp  = sum(1 for p in s.polls.values() if p["status"] == "draft")

        gender_counts = {}
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
        for v in s.voters.values():
            g = v.get("gender", "?")
            gender_counts[g] = gender_counts.get(g, 0) + 1
            age = v.get("age", 0)
            if age <= 25:   age_groups["18-25"] += 1
            elif age <= 35: age_groups["26-35"] += 1
            elif age <= 45: age_groups["36-45"] += 1
            elif age <= 55: age_groups["46-55"] += 1
            elif age <= 65: age_groups["56-65"] += 1
            else:           age_groups["65+"]   += 1

        party_counts = {}
        edu_counts   = {}
        for c in s.candidates.values():
            if c["is_active"]:
                party_counts[c["party"]]    = party_counts.get(c["party"], 0) + 1
                edu_counts[c["education"]]  = edu_counts.get(c["education"], 0) + 1

        station_load = {}
        for sid, st in s.voting_stations.items():
            vc = sum(1 for v in s.voters.values() if v["station_id"] == sid)
            lp = (vc / st["capacity"] * 100) if st["capacity"] > 0 else 0
            station_load[sid] = {
                "name":     st["name"],
                "voters":   vc,
                "capacity": st["capacity"],
                "load_pct": lp,
            }

        return {
            "total_candidates":   tc,  "active_candidates":   ac,
            "total_voters":       tv,  "verified_voters":     vv,
            "active_voters":      av,  "total_stations":      tst,
            "active_stations":    ast, "total_polls":         tp,
            "open_polls":         op,  "closed_polls":        cp,
            "draft_polls":        dp,  "total_votes":         len(s.votes),
            "gender_counts":      gender_counts,
            "age_groups":         age_groups,
            "party_counts":       party_counts,
            "edu_counts":         edu_counts,
            "station_load":       station_load,
        }
