"""
services/report_service.py
Responsibility: Generate reports and summaries (e.g., poll results).
Single responsibility: reporting. Can optionally log actions.
"""

from data.store import DataStore
from typing import Callable, Optional

class ReportService:
    def __init__(self, store: DataStore, log_action: Optional[Callable] = None):
        """
        :param store: Shared DataStore instance
        :param log_action: Optional callable to log actions, e.g., log_action(action, user, details)
        """
        self._store = store
        self._log_action = log_action

    # ── Poll reports ────────────────────────────────────────────────────────────
    def get_poll_results(self, poll_id: int) -> dict:
        """
        Returns a dictionary of candidate names to vote counts for the given poll.
        """
        poll = self._store.polls.get(poll_id)
        if not poll:
            if self._log_action:
                self._log_action("REPORT_FAILED", "SYSTEM", f"Poll {poll_id} not found")
            return {}

        # Count votes
        results = {}
        for candidate_id in poll.get("candidate_ids", []):
            candidate = self._store.candidates.get(candidate_id, {})
            name = candidate.get("full_name", f"Candidate {candidate_id}")
            vote_count = sum(1 for vote in self._store.votes if vote.get("poll_id") == poll_id and vote.get("candidate_id") == candidate_id)
            results[name] = vote_count

        if self._log_action:
            self._log_action("REPORT_VIEW", "SYSTEM", f"Poll {poll_id} results retrieved")

        return results

    # ── Additional reports can be added here ────────────────────────────────────
    def get_all_polls_summary(self) -> dict:
        """
        Returns a summary of all polls with total votes per poll.
        """
        summary = {}
        for poll_id, poll in self._store.polls.items():
            total_votes = sum(1 for vote in self._store.votes if vote.get("poll_id") == poll_id)
            summary[poll.get("title", f"Poll {poll_id}")] = total_votes

        if self._log_action:
            self._log_action("REPORT_VIEW", "SYSTEM", "All polls summary retrieved")

        return summary