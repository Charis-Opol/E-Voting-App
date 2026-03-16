"""
main.py - E-Voting System entry point.
Matches the original e_voting_console_app.py main() function.
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth_service import admin_login, voter_login, register_voter
from admin_dashboard import admin_dashboard
from voter_dashboard import voter_dashboard
from ui import clear_screen, header, menu_item, prompt, info, error, pause
from colors import THEME_LOGIN, RESET


def login():
    """Returns (user_dict, role_string) or (None, None)."""
    clear_screen()
    header("E-VOTING SYSTEM", THEME_LOGIN)
    print()
    menu_item(1, "Login as Admin", THEME_LOGIN)
    menu_item(2, "Login as Voter", THEME_LOGIN)
    menu_item(3, "Register as Voter", THEME_LOGIN)
    menu_item(4, "Exit", THEME_LOGIN)
    print()
    choice = prompt("Enter choice: ")

    if choice == "1":
        user = admin_login()
        return (user, "admin") if user else (None, None)
    elif choice == "2":
        user = voter_login()
        return (user, "voter") if user else (None, None)
    elif choice == "3":
        register_voter()
        return (None, None)
    elif choice == "4":
        print()
        info("Goodbye!")
        sys.exit(0)
    else:
        error("Invalid choice.")
        pause()
        return (None, None)


def main():
    print(f"\n  {THEME_LOGIN}Loading E-Voting System...{RESET}")

    while True:
        user, role = login()
        if user:
            if role == "admin":
                admin_dashboard(None, user)
            elif role == "voter":
                voter_dashboard(None, user)


if __name__ == "__main__":
    main()