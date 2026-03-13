"""
admin_dashboard.py - Admin dashboard with all management menus.
Uses DatabaseEngine for data access and delegates to StatsAndResults.
"""
from ui import UI
from stats_results import StatsAndResults
from colors import (RESET, BOLD, DIM, GREEN, RED, YELLOW,
                    THEME_ADMIN, THEME_ADMIN_ACCENT)

class AdminDashboard:
    def __init__(self, db, current_admin):
        self.db = db
        self.admin = current_admin
        self.ui = UI()
        self.stats = StatsAndResults(db, current_admin)

    def run(self):
        while True:
            self.ui.clear_screen()
            self.ui.header("ADMIN DASHBOARD", THEME_ADMIN)
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{self.admin['full_name']}{RESET}")
            print(f"  {DIM}    Role: {self.admin['role']}{RESET}")
            print()
            self.ui.menu_item(1, "View All Voters", THEME_ADMIN)
            self.ui.menu_item(2, "View All Candidates", THEME_ADMIN)
            self.ui.menu_item(3, "View All Polls", THEME_ADMIN)
            self.ui.menu_item(4, "View All Stations", THEME_ADMIN)
            self.ui.menu_item(5, "Stats & Results", THEME_ADMIN)
            self.ui.menu_item(6, "Logout", THEME_ADMIN)
            print()
            choice = self.ui.prompt("Enter choice: ")
            if   choice == "1": self._view_voters()
            elif choice == "2": self._view_candidates()
            elif choice == "3": self._view_polls()
            elif choice == "4": self._view_stations()
            elif choice == "5": self.stats.run()
            elif choice == "6":
                self.db.log_action("LOGOUT", self.admin["username"], "Admin logged out")
                break
            else: self.ui.error("Invalid option"); self.ui.pause()

    def _view_voters(self):
        self.ui.clear_screen()
        self.ui.header("ALL REGISTERED VOTERS", THEME_ADMIN)
        voters = self.db.get_all("voters")
        if not voters: print(); self.ui.info("No voters registered."); self.ui.pause(); return
        print()
        self.ui.table_header(
            f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}",
            THEME_ADMIN)
        self.ui.table_divider(70, THEME_ADMIN)
        for vid, v in voters.items():
            verified = self.ui.status_badge("Yes", True) if v["is_verified"] else self.ui.status_badge("No", False)
            active = self.ui.status_badge("Yes", True) if v["is_active"] else self.ui.status_badge("No", False)
            print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {v['station_id']:<6} {verified:<19} {active}")
        vc = sum(1 for v in voters.values() if v["is_verified"])
        uc = sum(1 for v in voters.values() if not v["is_verified"])
        print(f"\n  {DIM}Total: {len(voters)}  │  Verified: {vc}  │  Unverified: {uc}{RESET}")
        self.ui.pause()

    def _view_candidates(self):
        self.ui.clear_screen()
        self.ui.header("ALL CANDIDATES", THEME_ADMIN)
        candidates = self.db.get_all("candidates")
        if not candidates: print(); self.ui.info("No candidates."); self.ui.pause(); return
        print()
        for cid, c in candidates.items():
            status = self.ui.status_badge("Active", True) if c["is_active"] else self.ui.status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET} {status}")
        print(f"\n  {DIM}Total: {len(candidates)}{RESET}")
        self.ui.pause()

    def _view_polls(self):
        self.ui.clear_screen()
        self.ui.header("ALL POLLS / ELECTIONS", THEME_ADMIN)
        polls = self.db.get_all("polls")
        candidates = self.db.get_all("candidates")
        if not polls: print(); self.ui.info("No polls found."); self.ui.pause(); return
        for pid, poll in polls.items():
            sc = GREEN if poll['status']=='open' else (YELLOW if poll['status']=='draft' else RED)
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
            for pos in poll["positions"]:
                cn = [candidates[ccid]["full_name"] for ccid in pos["candidate_ids"] if ccid in candidates]
                cd = ", ".join(cn) if cn else f"{DIM}None assigned{RESET}"
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cd}")
        print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
        self.ui.pause()

    def _view_stations(self):
        self.ui.clear_screen()
        self.ui.header("ALL VOTING STATIONS", THEME_ADMIN)
        stations = self.db.get_all("voting_stations")
        if not stations: print(); self.ui.info("No stations."); self.ui.pause(); return
        print()
        for sid, s in stations.items():
            status = self.ui.status_badge("Active", True) if s["is_active"] else self.ui.status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET} {status}")
            print(f"     {DIM}Capacity: {s['capacity']} │ Supervisor: {s['supervisor']} │ Hours: {s['opening_time']}-{s['closing_time']}{RESET}")
        print(f"\n  {DIM}Total: {len(stations)}{RESET}")
        self.ui.pause()