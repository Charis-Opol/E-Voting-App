"""
main.py
Entry point. Wires all services together and starts the application loop.
This is the only file that knows about all layers — nothing else imports
from multiple layers simultaneously.
"""

import time
import sys
import os

# ── Make sure the evoting package root is on the path when run directly ──────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.console           import THEME_LOGIN, RESET, clear_screen
from data.store           import DataStore
from services.auth_service      import AuthService
from services.candidate_service import CandidateService
from services.station_service   import StationService
from services.position_service  import PositionService
from services.poll_service      import PollService
from services.voter_service     import VoterService
from services.admin_service     import AdminService
from services.vote_service      import VoteService
from ui.login_screen      import LoginScreen
from ui.admin_dashboard   import AdminDashboard
from ui.voter_dashboard   import VoterDashboard


def build_services(store: DataStore):
    """
    Constructs every service, injecting the shared store and the audit
    log callable so services never depend on each other directly.
    """
    auth_svc = AuthService(store)

    candidate_svc = CandidateService(store, auth_svc.log_action)
    station_svc   = StationService(store,   auth_svc.log_action)
    position_svc  = PositionService(store,  auth_svc.log_action)
    poll_svc      = PollService(store,      auth_svc.log_action)
    voter_svc     = VoterService(store,     auth_svc.log_action)
    admin_svc     = AdminService(store,     auth_svc.log_action, auth_svc.hash_password)
    vote_svc      = VoteService(store,      auth_svc.log_action)

    return auth_svc, candidate_svc, station_svc, position_svc, poll_svc, voter_svc, admin_svc, vote_svc


def main():
    # ── Bootstrap ────────────────────────────────────────────────────────────
    print(f"\n  {THEME_LOGIN}Loading E-Voting System...{RESET}")
    store = DataStore()
    store.load()
    time.sleep(1)

    (auth_svc, candidate_svc, station_svc,
     position_svc, poll_svc, voter_svc,
     admin_svc, vote_svc) = build_services(store)

    login_screen = LoginScreen(auth_svc, store)

    # ── Main application loop ────────────────────────────────────────────────
    while True:
        clear_screen()
        current_user, role = login_screen.run()

        if not current_user:
            continue  # bad login or registration — loop back

        if role == "admin":
            AdminDashboard(
                current_user  = current_user,
                candidate_svc = candidate_svc,
                station_svc   = station_svc,
                position_svc  = position_svc,
                poll_svc      = poll_svc,
                voter_svc     = voter_svc,
                admin_svc     = admin_svc,
                vote_svc      = vote_svc,
                auth_svc      = auth_svc,
                store         = store,
            ).run()

        elif role == "voter":
            VoterDashboard(
                current_user = current_user,
                vote_svc     = vote_svc,
                auth_svc     = auth_svc,
                store        = store,
            ).run()


if __name__ == "__main__":
    main()
