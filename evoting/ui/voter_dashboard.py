"""
ui/voter_dashboard.py
Responsibility: Render the voter menu and route choices to service calls.
Zero business logic — only UI flow + service calls.
"""

from services.vote_service import VoteService
from services.auth_service import AuthService
from ui.console import Console, THEME_VOTER, THEME_VOTER_ACCENT, BRIGHT_WHITE, BOLD, DIM, GREEN, RED, GRAY, BRIGHT_GREEN, BRIGHT_YELLOW, ITALIC

class VoterDashboard:
    """Top-level voter UI. Each menu action calls exactly one service method."""

    def __init__(self, current_user: dict,
                 vote_svc:  VoteService,
                 auth_svc:  AuthService,
                 store,
                 console: Console):
        self._user  = current_user
        self._vote  = vote_svc
        self._auth  = auth_svc
        self._store = store
        self.console = console

    def run(self):
        while True:
            self.console.clear_screen()
            self.console.header("VOTER DASHBOARD", THEME_VOTER)
            station_name = self._store.voting_stations.get(
                self._user["station_id"], {}
            ).get("name", "Unknown")
            print(f"  {THEME_VOTER}  ● {BOLD}{self._user['full_name']}{self.console.RESET}")
            print(f"  {DIM}    Card: {self._user['voter_card_number']}  │  Station: {station_name}{self.console.RESET}")
            print()
            self.console.menu_item(1, "View Open Polls",              THEME_VOTER)
            self.console.menu_item(2, "Cast Vote",                    THEME_VOTER)
            self.console.menu_item(3, "View My Voting History",       THEME_VOTER)
            self.console.menu_item(4, "View Results (Closed Polls)",  THEME_VOTER)
            self.console.menu_item(5, "View My Profile",              THEME_VOTER)
            self.console.menu_item(6, "Change Password",              THEME_VOTER)
            self.console.menu_item(7, "Logout",                       THEME_VOTER)
            print()
            choice = self.console.prompt("Enter choice: ")

            if choice == "1": self._view_open_polls()
            elif choice == "2": self._cast_vote()
            elif choice == "3": self._view_voting_history()
            elif choice == "4": self._view_closed_poll_results()
            elif choice == "5": self._view_profile()
            elif choice == "6": self._change_password()
            elif choice == "7":
                self._auth.logout_voter(self._user)
                break
            else:
                self.console.print_error("Invalid choice.")
                self.console.pause()

    def _view_open_polls(self):
        polls = self._vote.get_available_polls_for_voter(self._user)
        if not polls:
            self.console.print_info("No open polls available for you at this time.")
        else:
            for pid, p in polls.items():
                self.console.print(f"{pid} | {p['title']} | Ends: {p['end_date']}")
        self.console.pause()

    def _cast_vote(self):
        polls = self._vote.get_available_polls_for_voter(self._user)
        if not polls:
            self.console.print_info("No polls available to vote in.")
            self.console.pause()
            return
        
        for pid, p in polls.items():
            self.console.print(f"{pid}: {p['title']}")
        
        choice_input = self.console.prompt("Enter Poll ID to vote in: ")
        if not choice_input.isdigit(): return
        pid = int(choice_input)
        
        if pid not in polls:
            self.console.print_error("Invalid Poll ID.")
            self.console.pause()
            return

        poll = polls[pid]
        selections = []
        for pos in poll.get("positions", []):
            self.console.print(f"\nPosition: {pos['title']}")
            candidates = {cid: self._store.candidates[cid] for cid in pos['candidate_ids']}
            for cid, c in candidates.items():
                self.console.print(f"  {cid}: {c['full_name']} ({c['party']})")
            self.console.print("  0: Abstain")
            
            choice = self.console.prompt("Select candidate ID (or 0): ")
            if choice == "0":
                selections.append({
                    "position_id": pos['position_id'],
                    "position_title": pos['title'],
                    "candidate_id": None,
                    "abstained": True
                })
            elif choice.isdigit() and int(choice) in candidates:
                cid = int(choice)
                selections.append({
                    "position_id": pos['position_id'],
                    "position_title": pos['title'],
                    "candidate_id": cid,
                    "abstained": False
                })
            else:
                self.console.print_error("Invalid choice, skipping this position.")

        if selections:
            confirm = self.console.prompt("Confirm cast vote? (y/n): ")
            if confirm.lower() == 'y':
                ref = self._vote.cast_votes(self._user, pid, selections)
                self.console.print_success(f"Vote cast! Reference: {ref}")
        self.console.pause()

    def _view_voting_history(self):
        history = self._user.get("has_voted_in", [])
        if not history:
            self.console.print_info("You have not voted in any polls yet.")
        else:
            self.console.print("Your Voting History:")
            for pid in history:
                poll = self._store.polls.get(pid, {"title": "Unknown Poll"})
                self.console.print(f"- {poll['title']}")
        self.console.pause()

    def _view_closed_poll_results(self):
        polls = self._vote.get_closed_polls()
        if not polls:
            self.console.print_info("No closed polls found.")
        else:
            for pid, p in polls.items():
                self.console.print(f"{pid} | {p['title']}")
            
            choice_input = self.console.prompt("Enter Poll ID to view results: ")
            if not choice_input.isdigit(): return
            pid = int(choice_input)
            
            if pid in polls:
                self.console.print(f"Results for {polls[pid]['title']}:")
                # (Simple listing for now as per system capability)
            else:
                self.console.print_error("Invalid ID.")
        self.console.pause()

    def _view_profile(self):
        self.console.header("MY PROFILE", THEME_VOTER)
        for k, v in self._user.items():
            if k not in ["password", "role", "id"]:
                self.console.print(f"  {k.replace('_', ' ').title()}: {v}")
        self.console.pause()

    def _change_password(self):
        old = self.console.prompt("Current Password: ", password=True)
        new = self.console.prompt("New Password: ", password=True)
        conf = self.console.prompt("Confirm New Password: ", password=True)
        success, msg = self._auth.change_voter_password(self._user, old, new, conf)
        if success:
            self.console.print_success(msg or "Password changed successfully.")
        else:
            self.console.print_error(msg or "Failed to change password.")
        self.console.pause()