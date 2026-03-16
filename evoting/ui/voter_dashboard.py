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