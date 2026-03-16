"""
ui/login_screen.py
Responsibility: Render the login menu and collect credentials,
then delegate to AuthService. Returns the authenticated user + role.
"""

import datetime

from ui.console import (
    clear_screen, header, menu_item, prompt, masked_input, pause,
    print_error, print_success, print_warning, print_info, subheader,
    THEME_LOGIN, THEME_ADMIN, THEME_VOTER, BRIGHT_YELLOW, BOLD, RESET,
    BRIGHT_BLUE, DIM,
)
from services.auth_service import AuthService


class LoginScreen:
    """Handles the main entry screen: admin login, voter login, registration."""

    def __init__(self, auth_service: AuthService, store):
        self._auth  = auth_service
        self._store = store  # needed only to display station list during registration

    def run(self):
        """
        Shows the menu and processes the choice.
        Returns (user_dict, role_str) on successful login,
        or (None, None) to loop again.
        """
        clear_screen()
        header("E-VOTING SYSTEM", THEME_LOGIN)
        print()
        menu_item(1, "Login as Admin",   THEME_LOGIN)
        menu_item(2, "Login as Voter",   THEME_LOGIN)
        menu_item(3, "Register as Voter", THEME_LOGIN)
        menu_item(4, "Exit",             THEME_LOGIN)
        print()
        choice = prompt("Enter choice: ")

        if choice == "1":
            return self._admin_login()
        elif choice == "2":
            return self._voter_login()
        elif choice == "3":
            self._register_voter()
            return None, None
        elif choice == "4":
            print()
            print_info("Goodbye!")
            self._store.save()
            exit()
        else:
            print_error("Invalid choice.")
            pause()
            return None, None

    # ── Admin login ──────────────────────────────────────────────────────────

    def _admin_login(self):
        clear_screen()
        header("ADMIN LOGIN", THEME_ADMIN)
        print()
        username = prompt("Username: ")
        password = masked_input("Password: ").strip()

        user, err = self._auth.authenticate_admin(username, password)
        if user:
            print()
            print_success(f"Welcome, {user['full_name']}!")
            pause()
            return user, "admin"
        print_error(err)
        pause()
        return None, None

    # ── Voter login ──────────────────────────────────────────────────────────

    def _voter_login(self):
        clear_screen()
        header("VOTER LOGIN", THEME_VOTER)
        print()
        voter_card = prompt("Voter Card Number: ")
        password   = masked_input("Password: ").strip()

        user, err = self._auth.authenticate_voter(voter_card, password)
        if user:
            print()
            print_success(f"Welcome, {user['full_name']}!")
            pause()
            return user, "voter"
        if err and err.startswith("WARNING:"):
            print_warning(err[len("WARNING:"):])
            print_info("Please contact an admin to verify your registration.")
        else:
            print_error(err)
        pause()
        return None, None

    # ── Voter registration ───────────────────────────────────────────────────

    def _register_voter(self):
        clear_screen()
        header("VOTER REGISTRATION", THEME_VOTER)
        print()

        full_name   = prompt("Full Name: ")
        national_id = prompt("National ID Number: ")
        dob_str     = prompt("Date of Birth (YYYY-MM-DD): ")

        # Compute age here so we can display it in the error
        age = None
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            pass  # validation will catch this

        gender           = prompt("Gender (M/F/Other): ").upper()
        address          = prompt("Residential Address: ")
        phone            = prompt("Phone Number: ")
        email            = prompt("Email Address: ")
        password         = masked_input("Create Password: ").strip()
        confirm_password = masked_input("Confirm Password: ").strip()

        # Display stations before asking for station choice
        if not self._store.voting_stations:
            print_error("No voting stations available. Contact admin.")
            pause()
            return

        subheader("Available Voting Stations", THEME_VOTER)
        for sid, station in self._store.voting_stations.items():
            if station["is_active"]:
                print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station['name']} {DIM}- {station['location']}{RESET}")

        try:
            station_id = int(prompt("\nSelect your voting station ID: "))
        except ValueError:
            print_error("Invalid input.")
            pause()
            return

        ok, err = self._auth.validate_voter_registration(
            full_name, national_id, dob_str, gender,
            password, confirm_password, station_id,
        )
        if not ok:
            print_error(err)
            pause()
            return

        voter_card = self._auth.register_voter(
            full_name, national_id, dob_str, age,
            gender, address, phone, email, password, station_id,
        )
        print()
        print_success("Registration successful!")
        print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{voter_card}{RESET}")
        print_warning("IMPORTANT: Save this number! You need it to login.")
        print_info("Your registration is pending admin verification.")
        pause()
