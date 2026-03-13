"""
main.py - E-Voting System entry point.
Wires together the DatabaseEngine, AuthService, AdminDashboard,
VoterDashboard, and all sub-modules.
"""
import sys, os

# Ensure Frontend package imports work when run from Frontend/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_engine import DatabaseEngine
from auth_service import AuthService
from admin_dashboard import AdminDashboard
from voter_dashboard import VoterDashboard
from ui import UI
from colors import THEME_LOGIN, RESET, BRIGHT_CYAN

DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "database.json")

class EVotingSystem:
    def __init__(self):
        self.db   = DatabaseEngine(DATABASE_FILE)
        self.auth = AuthService(self.db)
        self.ui   = UI()

    def run(self):
        print(f"\n  {BRIGHT_CYAN}Loading E-Voting System...{RESET}")
        self.db.load()

        while True:
            self.ui.show_login_menu()
            choice = self.ui.prompt("Enter choice: ")

            if choice == "1":
                admin = self.auth.admin_login()
                if admin:
                    dashboard = AdminDashboard(self.db, admin)
                    dashboard.run()

            elif choice == "2":
                voter = self.auth.voter_login()
                if voter:
                    dashboard = VoterDashboard(self.db, voter)
                    dashboard.run()

            elif choice == "3":
                self.auth.register_voter()

            elif choice == "4":
                self.db.save()
                print()
                self.ui.info("Goodbye!")
                break
            else:
                self.ui.error("Invalid choice")

if __name__ == "__main__":
    system = EVotingSystem()
    system.run()