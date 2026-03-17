"""
auth_service.py - Authentication and registration using module-level UI functions.
Matches the exact interface of the original e_voting_console_app.py.
"""
from ui import (clear_screen, header, subheader, menu_item, prompt, masked_input,
                pause, error, success, warning, info, status_badge)
from colors import *

from Backend.admin_management import AuthenticateAdmin
from Backend.station_management import GetAllStations
from Backend.audits import LogAuditEntry

from frontend_service import AuthenticateVoter, RegisterVoterProcess

def admin_login():
    """Returns the admin dict on success, None on failure."""
    clear_screen()
    header("ADMIN LOGIN", THEME_ADMIN)
    print()
    username = prompt("Username: ")
    password = masked_input("Password: ").strip()
    
    try:
        admin = AuthenticateAdmin().execute(username, password)
        LogAuditEntry().execute("ADMIN_LOGIN", username, "Admin login successful")
        print(); success(f"Welcome, {admin['full_name']}!")
        pause(); return admin
    except ValueError as e:
        error(str(e))
        LogAuditEntry().execute("ADMIN_LOGIN_FAILED", username, str(e))
        pause(); return None

def voter_login():
    """Returns the voter dict on success, None on failure."""
    clear_screen()
    header("VOTER LOGIN", THEME_VOTER)
    print()
    voter_card = prompt("Voter Card Number: ")
    password = masked_input("Password: ").strip()
    
    try:
        voter = AuthenticateVoter().execute(voter_card, password)
        LogAuditEntry().execute("LOGIN", voter_card, "Voter login successful")
        print(); success(f"Welcome, {voter['full_name']}!")
        pause(); return voter
    except PermissionError as e:
        err_msg = str(e)
        if "verified" in err_msg.lower():
            warning("Your voter registration has not been verified yet.")
            info("Please contact an admin to verify your registration.")
            LogAuditEntry().execute("LOGIN_FAILED", voter_card, "Voter not verified")
        else:
            error(err_msg)
            LogAuditEntry().execute("LOGIN_FAILED", voter_card, "Voter account deactivated")
        pause(); return None
    except ValueError as e:
        error("Invalid voter card number or password.")
        LogAuditEntry().execute("LOGIN_FAILED", voter_card, "Invalid voter credentials")
        pause(); return None

def register_voter():
    """Register a new voter account."""
    clear_screen()
    header("VOTER REGISTRATION", THEME_VOTER)
    print()
    full_name = prompt("Full Name: ")
    if not full_name: error("Name cannot be empty."); pause(); return
    national_id = prompt("National ID Number: ")
    if not national_id: error("National ID cannot be empty."); pause(); return
    
    dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
    gender = prompt("Gender (M/F/Other): ").upper()
    if gender not in ["M", "F", "OTHER"]:
        error("Invalid gender selection."); pause(); return
        
    address = prompt("Residential Address: ")
    phone = prompt("Phone Number: ")
    email = prompt("Email Address: ")
    password = masked_input("Create Password: ").strip()
    confirm = masked_input("Confirm Password: ").strip()
    if password != confirm:
        error("Passwords do not match."); pause(); return
        
    stations = GetAllStations().execute()
    if not stations:
        error("No voting stations available. Contact admin."); pause(); return
        
    subheader("Available Voting Stations", THEME_VOTER)
    for s in stations:
        if s["is_active"]:
            print(f"    {BRIGHT_BLUE}{s['id']}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")
            
    try:
        station_choice = int(prompt("\nSelect your voting station ID: "))
    except ValueError:
        error("Invalid input."); pause(); return
        
    try:
        voter_record = RegisterVoterProcess().execute(
            full_name=full_name, national_id=national_id, dob_str=dob_str,
            gender=gender, address=address, phone=phone, email=email,
            plain_password=password, station_id=station_choice
        )
        voter_card = voter_record["voter_card_number"]
        LogAuditEntry().execute("REGISTER", full_name, f"New voter registered with card: {voter_card}")
        
        print()
        success("Registration successful!")
        print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{voter_card}{RESET}")
        warning("IMPORTANT: Save this number! You need it to login.")
        info("Your registration is pending admin verification.")
    except ValueError as e:
        error(str(e))
    pause()