"""
ui/login_screen.py
Responsibility: Render the login menu and collect credentials,
then delegate to AuthService. Returns the authenticated user + role.
"""

import datetime
from services.auth_service import AuthService
from ui.console import Console, THEME_LOGIN, THEME_ADMIN, THEME_VOTER, BRIGHT_YELLOW

class LoginScreen:
    """Handles the main entry screen: admin login, voter login, registration."""

    def __init__(self, auth_service: AuthService, store, console: Console):
        self._auth = auth_service
        self._store = store
        self.console = console

    def run(self):
        self.console.clear_screen()
        self.console.header("E-VOTING SYSTEM", THEME_LOGIN)
        print()
        self.console.menu_item(1, "Login as Admin",   THEME_LOGIN)
        self.console.menu_item(2, "Login as Voter",   THEME_LOGIN)
        self.console.menu_item(3, "Register as Voter", THEME_LOGIN)
        self.console.menu_item(4, "Exit",             THEME_LOGIN)
        print()
        choice = self.console.prompt("Enter choice: ")

        if choice == "1":
            return self._admin_login()
        elif choice == "2":
            return self._voter_login()
        elif choice == "3":
            self._register_voter()
            return None, None
        elif choice == "4":
            print()
            self.console.print_info("Goodbye!")
            self._store.save()
            exit()
        else:
            self.console.print_error("Invalid choice.")
            self.console.pause()
            return None, None

    # ── Admin login ──────────────────────────────────────────────────────────
    def _admin_login(self):
        self.console.clear_screen()
        self.console.header("ADMIN LOGIN", THEME_ADMIN)
        print()
        username = self.console.prompt("Username: ")
        password = self.console.masked_input("Password: ").strip()

        user, err = self._auth.authenticate_admin(username, password)
        if user:
            print()
            self.console.print_success(f"Welcome, {user['full_name']}!")
            self.console.pause()
            return user, "admin"
        self.console.print_error(err)
        self.console.pause()
        return None, None

    # ── Voter login ──────────────────────────────────────────────────────────
    def _voter_login(self):
        self.console.clear_screen()
        self.console.header("VOTER LOGIN", THEME_VOTER)
        print()
        voter_card = self.console.prompt("Voter Card Number: ")
        password   = self.console.masked_input("Password: ").strip()

        user, err = self._auth.authenticate_voter(voter_card, password)
        if user:
            print()
            self.console.print_success(f"Welcome, {user['full_name']}!")
            self.console.pause()
            return user, "voter"
        if err and err.startswith("WARNING:"):
            self.console.print_warning(err[len("WARNING:"):])
            self.console.print_info("Please contact an admin to verify your registration.")
        else:
            self.console.print_error(err)
        self.console.pause()
        return None, None

    # ── Voter registration ───────────────────────────────────────────────────
    def _register_voter(self):
        self.console.clear_screen()
        self.console.header("VOTER REGISTRATION", THEME_VOTER)
        print()

        full_name   = self.console.prompt("Full Name: ")
        national_id = self.console.prompt("National ID Number: ")
        dob_str     = self.console.prompt("Date of Birth (YYYY-MM-DD): ")

        age = None
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            pass

        gender           = self.console.prompt("Gender (M/F/Other): ").upper()
        address          = self.console.prompt("Residential Address: ")
        phone            = self.console.prompt("Phone Number: ")
        email            = self.console.prompt("Email Address: ")
        password         = self.console.masked_input("Create Password: ").strip()
        confirm_password = self.console.masked_input("Confirm Password: ").strip()

        if not self._store.voting_stations:
            self.console.print_error("No voting stations available. Contact admin.")
            self.console.pause()
            return

        self.console.subheader("Available Voting Stations", THEME_VOTER)
        for sid, station in self._store.voting_stations.items():
            if station["is_active"]:
                print(f"    {BRIGHT_YELLOW}{sid}.{full_name}{self.console.RESET} {station['name']} - {station['location']}")

        try:
            station_id = int(self.console.prompt("\nSelect your voting station ID: "))
        except ValueError:
            self.console.print_error("Invalid input.")
            self.console.pause()
            return

        ok, err = self._auth.validate_voter_registration(
            full_name, national_id, dob_str, gender,
            password, confirm_password, station_id,
        )
        if not ok:
            self.console.print_error(err)
            self.console.pause()
            return

        voter_card = self._auth.register_voter(
            full_name, national_id, dob_str, age,
            gender, address, phone, email, password, station_id,
        )
        print()
        self.console.print_success("Registration successful!")
        print(f"  Your Voter Card Number: {BRIGHT_YELLOW}{voter_card}{self.console.RESET}")
        self.console.print_warning("IMPORTANT: Save this number! You need it to login.")
        self.console.print_info("Your registration is pending admin verification.")
        self.console.pause()