"""
auth_service.py - Authentication and registration.
All data access goes through the DatabaseEngine API.
"""
import random, string, datetime
from security import hash_password
from ui import UI
from colors import (RESET, BOLD, DIM, BRIGHT_BLUE, BRIGHT_YELLOW,
                    THEME_ADMIN, THEME_VOTER)

MIN_VOTER_AGE = 18

class AuthService:
    def __init__(self, db):
        self.db = db
        self.ui = UI()

    def admin_login(self):
        self.ui.clear_screen()
        self.ui.header("ADMIN LOGIN", THEME_ADMIN)
        print()
        username = self.ui.prompt("Username: ")
        password = self.ui.masked_input("Password: ").strip()
        hashed = hash_password(password)
        admins = self.db.get_all("admins")
        for aid, admin in admins.items():
            if admin["username"] == username and admin["password"] == hashed:
                if not admin["is_active"]:
                    self.ui.error("This account has been deactivated.")
                    self.db.log_action("LOGIN_FAILED", username, "Account deactivated")
                    self.ui.pause(); return None
                self.db.log_action("LOGIN", username, "Admin login successful")
                print(); self.ui.success(f"Welcome, {admin['full_name']}!")
                self.ui.pause(); return admin
        self.ui.error("Invalid credentials.")
        self.db.log_action("LOGIN_FAILED", username, "Invalid admin credentials")
        self.ui.pause(); return None

    def voter_login(self):
        self.ui.clear_screen()
        self.ui.header("VOTER LOGIN", THEME_VOTER)
        print()
        voter_card = self.ui.prompt("Voter Card Number: ")
        password = self.ui.masked_input("Password: ").strip()
        hashed = hash_password(password)
        voters = self.db.get_all("voters")
        for vid, voter in voters.items():
            if voter["voter_card_number"] == voter_card and voter["password"] == hashed:
                if not voter["is_active"]:
                    self.ui.error("This voter account has been deactivated.")
                    self.db.log_action("LOGIN_FAILED", voter_card, "Voter account deactivated")
                    self.ui.pause(); return None
                if not voter["is_verified"]:
                    self.ui.warning("Your registration has not been verified yet.")
                    self.ui.info("Please contact an admin to verify.")
                    self.db.log_action("LOGIN_FAILED", voter_card, "Voter not verified")
                    self.ui.pause(); return None
                self.db.log_action("LOGIN", voter_card, "Voter login successful")
                print(); self.ui.success(f"Welcome, {voter['full_name']}!")
                self.ui.pause(); return voter
        self.ui.error("Invalid voter card number or password.")
        self.db.log_action("LOGIN_FAILED", voter_card, "Invalid voter credentials")
        self.ui.pause(); return None

    def register_voter(self):
        self.ui.clear_screen()
        self.ui.header("VOTER REGISTRATION", THEME_VOTER)
        print()
        full_name = self.ui.prompt("Full Name: ")
        if not full_name: self.ui.error("Name cannot be empty."); self.ui.pause(); return
        national_id = self.ui.prompt("National ID Number: ")
        if not national_id: self.ui.error("National ID cannot be empty."); self.ui.pause(); return
        voters = self.db.get_all("voters")
        for vid, v in voters.items():
            if v["national_id"] == national_id:
                self.ui.error("A voter with this National ID already exists."); self.ui.pause(); return
        dob_str = self.ui.prompt("Date of Birth (YYYY-MM-DD): ")
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
            if age < MIN_VOTER_AGE:
                self.ui.error(f"Must be at least {MIN_VOTER_AGE} years old."); self.ui.pause(); return
        except ValueError:
            self.ui.error("Invalid date format."); self.ui.pause(); return
        gender = self.ui.prompt("Gender (M/F/Other): ").upper()
        if gender not in ["M", "F", "OTHER"]:
            self.ui.error("Invalid gender."); self.ui.pause(); return
        address = self.ui.prompt("Residential Address: ")
        phone = self.ui.prompt("Phone Number: ")
        email = self.ui.prompt("Email Address: ")
        password = self.ui.masked_input("Create Password: ").strip()
        if len(password) < 6:
            self.ui.error("Password must be at least 6 characters."); self.ui.pause(); return
        confirm = self.ui.masked_input("Confirm Password: ").strip()
        if password != confirm:
            self.ui.error("Passwords do not match."); self.ui.pause(); return
        stations = self.db.get_all("voting_stations")
        if not stations:
            self.ui.error("No voting stations available."); self.ui.pause(); return
        self.ui.subheader("Available Voting Stations", THEME_VOTER)
        for sid, s in stations.items():
            if s["is_active"]:
                print(f"    {BRIGHT_BLUE}{sid}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")
        try:
            sc = int(self.ui.prompt("Select your voting station ID: "))
            if sc not in stations or not stations[sc]["is_active"]:
                self.ui.error("Invalid station."); self.ui.pause(); return
        except ValueError:
            self.ui.error("Invalid input."); self.ui.pause(); return
        voter_card = "".join(random.choices(string.ascii_uppercase + string.digits, k=12))
        vid = self.db.get_next_id("voters")
        rec = {
            "id": vid, "full_name": full_name, "national_id": national_id,
            "date_of_birth": dob_str, "age": age, "gender": gender,
            "address": address, "phone": phone, "email": email,
            "password": hash_password(password), "voter_card_number": voter_card,
            "station_id": sc, "is_verified": False, "is_active": True,
            "has_voted_in": [], "registered_at": str(datetime.datetime.now()), "role": "voter",
        }
        self.db.insert("voters", vid, rec)
        self.db.increment_counter("voters")
        self.db.log_action("REGISTER", full_name, f"New voter registered with card: {voter_card}")
        print(); self.ui.success("Registration successful!")
        print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{voter_card}{RESET}")
        self.ui.warning("IMPORTANT: Save this number! You need it to login.")
        self.ui.info("Your registration is pending admin verification.")
        self.ui.pause()