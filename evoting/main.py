"""
main.py
Entry point of the E-Voting System.
This wires all services together and starts the application loop.
Only this file knows about all layers — other modules remain decoupled.
"""

import time
import sys
import os

# Ensure evoting package root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# UI and console
from ui.console           import THEME_LOGIN, RESET, Console
from ui.login_screen      import LoginScreen
from ui.admin_dashboard   import AdminDashboard
from ui.voter_dashboard   import VoterDashboard

# Data layer
from data.store           import DataStore

# Services
from services.auth_service      import AuthService
from services.candidate_service import CandidateService
from services.station_service   import StationService
from services.position_service  import PositionService
from services.poll_service      import PollService
from services.voter_service     import VoterService
from services.admin_service     import AdminService
from services.vote_service      import VoteService
from services.report_service    import ReportService

# UI wrappers for dashboards
from ui.admin.candidate_ui import CandidateUI
from ui.admin.station_ui   import StationUI
from ui.admin.poll_ui      import PollUI
from ui.admin.voter_ui     import VoterUI
from ui.admin.admin_ui     import AdminUI
from ui.admin.report_ui    import ReportUI


def build_services(store: DataStore):
    """
    Constructs all services, injecting the shared data store and audit log callable.
    No service depends directly on another service.
    """
    auth_svc     = AuthService(store)
    candidate_svc = CandidateService(store, auth_svc.log_action)
    station_svc   = StationService(store,   auth_svc.log_action)
    position_svc  = PositionService(store,  auth_svc.log_action)
    poll_svc      = PollService(store,      auth_svc.log_action)
    voter_svc     = VoterService(store,     auth_svc.log_action)
    admin_svc     = AdminService(store,     auth_svc.log_action, auth_svc.hash_password)
    vote_svc      = VoteService(store,      auth_svc.log_action)
    report_svc    = ReportService(store,    auth_svc.log_action)

    return auth_svc, candidate_svc, station_svc, position_svc, poll_svc, voter_svc, admin_svc, vote_svc, report_svc


def build_ui(console, services):
    """
    Wrap all service objects in UI layers to handle user input/output.
    Returns a dictionary of UI objects for the dashboard.
    """
    (auth_svc, candidate_svc, station_svc,
     position_svc, poll_svc, voter_svc,
     admin_svc, vote_svc, report_svc) = services

    candidate_ui = CandidateUI(candidate_svc, console)
    station_ui   = StationUI(station_svc, console)
    poll_ui      = PollUI(poll_svc, console)
    voter_ui     = VoterUI(voter_svc, auth_svc, console)
    admin_ui     = AdminUI(admin_svc, console)
    report_ui    = ReportUI(poll_svc, console)

    return {
        "candidate_ui": candidate_ui,
        "station_ui": station_ui,
        "poll_ui": poll_ui,
        "voter_ui": voter_ui,
        "admin_ui": admin_ui,
        "report_ui": report_ui,
        "auth_svc": auth_svc,
        "vote_svc": vote_svc
    }


def main():
    # Bootstrap
    console = Console()  # Console object for all dashboards
    print(f"\n  {THEME_LOGIN}Loading E-Voting System...{RESET}")

    store = DataStore()
    store.load()
    time.sleep(1)

    # Build services
    services = build_services(store)

    # Build UI wrappers
    ui = build_ui(console, services)

    # Build login screen
    login_screen = LoginScreen(ui["auth_svc"], store, console)

    # Main application loop
    while True:
        console.clear_screen()
        current_user, role = login_screen.run()  # returns (user_dict, role_str)

        if not current_user:
            continue  # Invalid login — loop back

        if role == "admin":
            AdminDashboard(
                console      = console,
                candidate_ui = ui["candidate_ui"],
                station_ui   = ui["station_ui"],
                poll_ui      = ui["poll_ui"],
                voter_ui     = ui["voter_ui"],
                admin_ui     = ui["admin_ui"],
                report_ui    = ui["report_ui"],
                current_user = current_user
            ).show()

        elif role == "voter":
            VoterDashboard(
                console      = console,
                vote_svc     = ui["vote_svc"],
                auth_svc     = ui["auth_svc"],
                store        = store,
                current_user = current_user
            ).run()


if __name__ == "__main__":
    main()