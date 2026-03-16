"""
ui/admin_dashboard.py
Responsibility: Render the admin menu and route choices to service calls.
Zero business logic — only UI flow + service calls.
"""

from ui.console import (
    clear_screen, header, subheader, menu_item, prompt, pause,
    print_error, print_success, print_warning, print_info,
    table_header, table_divider, status_badge,
    THEME_ADMIN, THEME_ADMIN_ACCENT, BOLD, DIM, RESET,
    GREEN, YELLOW, RED, GRAY, BG_GREEN, BLACK, BRIGHT_WHITE,
    BRIGHT_YELLOW, BRIGHT_CYAN, ITALIC, THEME_VOTER,
    masked_input,
)
from services.candidate_service import CandidateService, REQUIRED_EDUCATION_LEVELS, MIN_CANDIDATE_AGE
from services.station_service   import StationService
from services.position_service  import PositionService
from services.poll_service      import PollService
from services.voter_service     import VoterService
from services.admin_service     import AdminService, ADMIN_ROLES
from services.vote_service      import VoteService


class AdminDashboard:
    """Top-level admin UI. Each menu action calls exactly one service method."""

    def __init__(self, current_user: dict,
                 candidate_svc: CandidateService,
                 station_svc:   StationService,
                 position_svc:  PositionService,
                 poll_svc:      PollService,
                 voter_svc:     VoterService,
                 admin_svc:     AdminService,
                 vote_svc:      VoteService,
                 auth_svc,
                 store):
        self._user         = current_user
        self._candidate    = candidate_svc
        self._station      = station_svc
        self._position     = position_svc
        self._poll         = poll_svc
        self._voter        = voter_svc
        self._admin        = admin_svc
        self._vote         = vote_svc
        self._auth         = auth_svc
        self._store        = store   # read-only reference for display helpers

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        while True:
            clear_screen()
            header("ADMIN DASHBOARD", THEME_ADMIN)
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{self._user['full_name']}{RESET}"
                  f"  {DIM}│  Role: {self._user['role']}{RESET}")

            subheader("Candidate Management",       THEME_ADMIN_ACCENT)
            menu_item(1,  "Create Candidate",        THEME_ADMIN)
            menu_item(2,  "View All Candidates",     THEME_ADMIN)
            menu_item(3,  "Update Candidate",        THEME_ADMIN)
            menu_item(4,  "Delete Candidate",        THEME_ADMIN)
            menu_item(5,  "Search Candidates",       THEME_ADMIN)

            subheader("Voting Station Management",   THEME_ADMIN_ACCENT)
            menu_item(6,  "Create Voting Station",   THEME_ADMIN)
            menu_item(7,  "View All Stations",       THEME_ADMIN)
            menu_item(8,  "Update Station",          THEME_ADMIN)
            menu_item(9,  "Delete Station",          THEME_ADMIN)

            subheader("Polls & Positions",           THEME_ADMIN_ACCENT)
            menu_item(10, "Create Position",         THEME_ADMIN)
            menu_item(11, "View Positions",          THEME_ADMIN)
            menu_item(12, "Update Position",         THEME_ADMIN)
            menu_item(13, "Delete Position",         THEME_ADMIN)
            menu_item(14, "Create Poll",             THEME_ADMIN)
            menu_item(15, "View All Polls",          THEME_ADMIN)
            menu_item(16, "Update Poll",             THEME_ADMIN)
            menu_item(17, "Delete Poll",             THEME_ADMIN)
            menu_item(18, "Open/Close Poll",         THEME_ADMIN)
            menu_item(19, "Assign Candidates to Poll", THEME_ADMIN)

            subheader("Voter Management",            THEME_ADMIN_ACCENT)
            menu_item(20, "View All Voters",         THEME_ADMIN)
            menu_item(21, "Verify Voter",            THEME_ADMIN)
            menu_item(22, "Deactivate Voter",        THEME_ADMIN)
            menu_item(23, "Search Voters",           THEME_ADMIN)

            subheader("Admin Management",            THEME_ADMIN_ACCENT)
            menu_item(24, "Create Admin Account",    THEME_ADMIN)
            menu_item(25, "View Admins",             THEME_ADMIN)
            menu_item(26, "Deactivate Admin",        THEME_ADMIN)

            subheader("Results & Reports",           THEME_ADMIN_ACCENT)
            menu_item(27, "View Poll Results",       THEME_ADMIN)
            menu_item(28, "View Detailed Statistics", THEME_ADMIN)
            menu_item(29, "View Audit Log",          THEME_ADMIN)
            menu_item(30, "Station-wise Results",    THEME_ADMIN)

            subheader("System",                      THEME_ADMIN_ACCENT)
            menu_item(31, "Save Data",               THEME_ADMIN)
            menu_item(32, "Logout",                  THEME_ADMIN)
            print()
            choice = prompt("Enter choice: ")

            actions = {
                "1":  self._create_candidate,
                "2":  self._view_all_candidates,
                "3":  self._update_candidate,
                "4":  self._delete_candidate,
                "5":  self._search_candidates,
                "6":  self._create_station,
                "7":  self._view_all_stations,
                "8":  self._update_station,
                "9":  self._delete_station,
                "10": self._create_position,
                "11": self._view_positions,
                "12": self._update_position,
                "13": self._delete_position,
                "14": self._create_poll,
                "15": self._view_all_polls,
                "16": self._update_poll,
                "17": self._delete_poll,
                "18": self._open_close_poll,
                "19": self._assign_candidates_to_poll,
                "20": self._view_all_voters,
                "21": self._verify_voter,
                "22": self._deactivate_voter,
                "23": self._search_voters,
                "24": self._create_admin,
                "25": self._view_admins,
                "26": self._deactivate_admin,
                "27": self._view_poll_results,
                "28": self._view_detailed_statistics,
                "29": self._view_audit_log,
                "30": self._station_wise_results,
            }
            if choice in actions:
                actions[choice]()
            elif choice == "31":
                self._store.save()
                pause()
            elif choice == "32":
                self._auth.logout_admin(self._user)
                break
            else:
                print_error("Invalid choice.")
                pause()

    # ══════════════════════════════════════════════════════════════════════════
    # CANDIDATE SCREENS
    # ══════════════════════════════════════════════════════════════════════════

    def _create_candidate(self):
        clear_screen()
        header("CREATE NEW CANDIDATE", THEME_ADMIN)
        print()
        full_name    = prompt("Full Name: ")
        national_id  = prompt("National ID: ")
        dob_str      = prompt("Date of Birth (YYYY-MM-DD): ")
        gender       = prompt("Gender (M/F/Other): ").upper()

        subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        try:
            edu_choice = int(prompt("Select education level: "))
            if edu_choice < 1 or edu_choice > len(REQUIRED_EDUCATION_LEVELS):
                print_error("Invalid choice."); pause(); return
            education = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        except ValueError:
            print_error("Invalid input."); pause(); return

        party           = prompt("Political Party/Affiliation: ")
        manifesto       = prompt("Brief Manifesto/Bio: ")
        address         = prompt("Address: ")
        phone           = prompt("Phone: ")
        email           = prompt("Email: ")
        criminal_record = prompt("Has Criminal Record? (yes/no): ").lower()
        years_exp_raw   = prompt("Years of Public Service/Political Experience: ")
        try:
            years_experience = int(years_exp_raw)
        except ValueError:
            years_experience = 0

        import datetime as _dt
        try:
            dob = _dt.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (_dt.datetime.now() - dob).days // 365
        except ValueError:
            print_error("Invalid date format."); pause(); return

        age_val, err = self._candidate.validate_candidate(full_name, national_id, dob_str, criminal_record)
        if err:
            if err.startswith("REJECTED:"):
                self._auth.log_action("CANDIDATE_REJECTED", self._user["username"],
                                      f"Candidate {full_name} rejected - criminal record")
                print_error(err[len("REJECTED:"):])
            else:
                print_error(err)
            pause(); return

        cid = self._candidate.create_candidate(
            full_name, national_id, dob_str, age_val, gender, education,
            party, manifesto, address, phone, email, years_experience,
            self._user["username"],
        )
        print()
        print_success(f"Candidate '{full_name}' created successfully! ID: {cid}")
        pause()

    def _view_all_candidates(self):
        clear_screen()
        header("ALL CANDIDATES", THEME_ADMIN)
        candidates = self._candidate.get_all_candidates()
        if not candidates:
            print(); print_info("No candidates found."); pause(); return
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}", THEME_ADMIN)
        table_divider(85, THEME_ADMIN)
        for c in candidates.values():
            badge = status_badge("Active", True) if c["is_active"] else status_badge("Inactive", False)
            print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20} {badge}")
        print(f"\n  {DIM}Total Candidates: {len(candidates)}{RESET}")
        pause()

    def _update_candidate(self):
        clear_screen()
        header("UPDATE CANDIDATE", THEME_ADMIN)
        candidates = self._candidate.get_all_candidates()
        if not candidates:
            print(); print_info("No candidates found."); pause(); return
        print()
        for c in candidates.values():
            print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
        try:
            cid = int(prompt("\nEnter Candidate ID to update: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        c = self._candidate.get_candidate_by_id(cid)
        if not c:
            print_error("Candidate not found."); pause(); return

        print(f"\n  {BOLD}Updating: {c['full_name']}{RESET}")
        print_info("Press Enter to keep current value\n")

        updates = {
            "full_name":        prompt(f"Full Name [{c['full_name']}]: "),
            "party":            prompt(f"Party [{c['party']}]: "),
            "manifesto":        prompt(f"Manifesto [{c['manifesto'][:50]}...]: "),
            "phone":            prompt(f"Phone [{c['phone']}]: "),
            "email":            prompt(f"Email [{c['email']}]: "),
            "address":          prompt(f"Address [{c['address']}]: "),
        }
        exp_raw = prompt(f"Years Experience [{c['years_experience']}]: ")
        if exp_raw:
            try:
                updates["years_experience"] = int(exp_raw)
            except ValueError:
                print_warning("Invalid number, keeping old value.")
                updates.pop("years_experience", None)

        self._candidate.update_candidate(cid, updates, self._user["username"])
        print(); print_success(f"Candidate '{c['full_name']}' updated successfully!")
        pause()

    def _delete_candidate(self):
        clear_screen()
        header("DELETE CANDIDATE", THEME_ADMIN)
        candidates = self._candidate.get_all_candidates()
        if not candidates:
            print(); print_info("No candidates found."); pause(); return
        print()
        for c in candidates.values():
            badge = status_badge("Active", True) if c["is_active"] else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET} {badge}")
        try:
            cid = int(prompt("\nEnter Candidate ID to delete: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        if not self._candidate.get_candidate_by_id(cid):
            print_error("Candidate not found."); pause(); return
        name = self._store.candidates[cid]["full_name"]
        confirm = prompt(f"Are you sure you want to delete '{name}'? (yes/no): ").lower()
        if confirm == "yes":
            ok, result = self._candidate.deactivate_candidate(cid, self._user["username"])
            if ok:
                print(); print_success(f"Candidate '{result}' has been deactivated.")
            else:
                print_error(result)
        else:
            print_info("Deletion cancelled.")
        pause()

    def _search_candidates(self):
        clear_screen()
        header("SEARCH CANDIDATES", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name",            THEME_ADMIN)
        menu_item(2, "Party",           THEME_ADMIN)
        menu_item(3, "Education Level", THEME_ADMIN)
        menu_item(4, "Age Range",       THEME_ADMIN)
        choice = prompt("\nChoice: ")

        results = []
        if choice == "1":
            term = prompt("Enter name to search: ")
            results = self._candidate.search_by_name(term)
        elif choice == "2":
            term = prompt("Enter party name: ")
            results = self._candidate.search_by_party(term)
        elif choice == "3":
            subheader("Education Levels", THEME_ADMIN_ACCENT)
            for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
            try:
                edu_choice = int(prompt("Select: "))
                edu = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
                results = self._candidate.search_by_education(edu)
            except (ValueError, IndexError):
                print_error("Invalid choice."); pause(); return
        elif choice == "4":
            try:
                min_age = int(prompt("Min age: "))
                max_age = int(prompt("Max age: "))
                results = self._candidate.search_by_age_range(min_age, max_age)
            except ValueError:
                print_error("Invalid input."); pause(); return
        else:
            print_error("Invalid choice."); pause(); return

        if not results:
            print(); print_info("No candidates found matching your criteria.")
        else:
            print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
            table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}", THEME_ADMIN)
            table_divider(75, THEME_ADMIN)
            for c in results:
                print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20}")
        pause()

    # ══════════════════════════════════════════════════════════════════════════
    # STATION SCREENS
    # ══════════════════════════════════════════════════════════════════════════

    def _create_station(self):
        clear_screen()
        header("CREATE VOTING STATION", THEME_ADMIN)
        print()
        name     = prompt("Station Name: ")
        if not name: print_error("Name cannot be empty."); pause(); return
        location = prompt("Location/Address: ")
        if not location: print_error("Location cannot be empty."); pause(); return
        region   = prompt("Region/District: ")
        try:
            capacity = int(prompt("Voter Capacity: "))
            if capacity <= 0: print_error("Capacity must be positive."); pause(); return
        except ValueError:
            print_error("Invalid capacity."); pause(); return
        supervisor   = prompt("Station Supervisor Name: ")
        contact      = prompt("Contact Phone: ")
        opening_time = prompt("Opening Time (e.g. 08:00): ")
        closing_time = prompt("Closing Time (e.g. 17:00): ")

        sid = self._station.create_station(
            name, location, region, capacity, supervisor, contact,
            opening_time, closing_time, self._user["username"],
        )
        print(); print_success(f"Voting Station '{name}' created! ID: {sid}")
        pause()

    def _view_all_stations(self):
        clear_screen()
        header("ALL VOTING STATIONS", THEME_ADMIN)
        stations = self._station.get_all_stations()
        if not stations:
            print(); print_info("No voting stations found."); pause(); return
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}",
            THEME_ADMIN,
        )
        table_divider(96, THEME_ADMIN)
        for s in stations.values():
            reg_count = self._station.get_registered_voter_count(s["id"])
            badge = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
            print(f"  {s['id']:<5} {s['name']:<25} {s['location']:<25} {s['region']:<15}"
                  f" {s['capacity']:<8} {reg_count:<8} {badge}")
        print(f"\n  {DIM}Total Stations: {len(stations)}{RESET}")
        pause()

    def _update_station(self):
        clear_screen()
        header("UPDATE VOTING STATION", THEME_ADMIN)
        stations = self._station.get_all_stations()
        if not stations:
            print(); print_info("No stations found."); pause(); return
        print()
        for s in stations.values():
            print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")
        try:
            sid = int(prompt("\nEnter Station ID to update: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        s = self._station.get_station_by_id(sid)
        if not s:
            print_error("Station not found."); pause(); return

        print(f"\n  {BOLD}Updating: {s['name']}{RESET}")
        print_info("Press Enter to keep current value\n")
        updates = {
            "name":       prompt(f"Name [{s['name']}]: "),
            "location":   prompt(f"Location [{s['location']}]: "),
            "region":     prompt(f"Region [{s['region']}]: "),
            "supervisor": prompt(f"Supervisor [{s['supervisor']}]: "),
            "contact":    prompt(f"Contact [{s['contact']}]: "),
        }
        cap_raw = prompt(f"Capacity [{s['capacity']}]: ")
        if cap_raw:
            try:
                updates["capacity"] = int(cap_raw)
            except ValueError:
                print_warning("Invalid number, keeping old value.")
        self._station.update_station(sid, updates, self._user["username"])
        print(); print_success(f"Station '{s['name']}' updated successfully!")
        pause()

    def _delete_station(self):
        clear_screen()
        header("DELETE VOTING STATION", THEME_ADMIN)
        stations = self._station.get_all_stations()
        if not stations:
            print(); print_info("No stations found."); pause(); return
        print()
        for s in stations.values():
            badge = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET} {badge}")
        try:
            sid = int(prompt("\nEnter Station ID to delete: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        if not self._station.get_station_by_id(sid):
            print_error("Station not found."); pause(); return

        voter_count = self._station.get_registered_voter_count(sid)
        if voter_count > 0:
            print_warning(f"{voter_count} voters are registered at this station.")
            if prompt("Proceed with deactivation? (yes/no): ").lower() != "yes":
                print_info("Cancelled."); pause(); return

        if prompt(f"Confirm deactivation of '{stations[sid]['name']}'? (yes/no): ").lower() == "yes":
            _, name = self._station.deactivate_station(sid, self._user["username"])
            print(); print_success(f"Station '{name}' deactivated.")
        else:
            print_info("Cancelled.")
        pause()

    # ══════════════════════════════════════════════════════════════════════════
    # POSITION SCREENS
    # ══════════════════════════════════════════════════════════════════════════

    def _create_position(self):
        clear_screen()
        header("CREATE POSITION", THEME_ADMIN)
        print()
        title = prompt("Position Title (e.g. President, Governor, Senator): ")
        if not title: print_error("Title cannot be empty."); pause(); return
        description = prompt("Description: ")
        level = prompt("Level (National/Regional/Local): ")
        if level.lower() not in ("national", "regional", "local"):
            print_error("Invalid level."); pause(); return
        try:
            max_winners = int(prompt("Number of winners/seats: "))
            if max_winners <= 0: print_error("Must be at least 1."); pause(); return
        except ValueError:
            print_error("Invalid number."); pause(); return
        min_age_raw = prompt(f"Minimum candidate age [{MIN_CANDIDATE_AGE}]: ")
        min_cand_age = int(min_age_raw) if min_age_raw.isdigit() else MIN_CANDIDATE_AGE

        pid = self._position.create_position(
            title, description, level, max_winners, min_cand_age,
            self._user["username"],
        )
        print(); print_success(f"Position '{title}' created! ID: {pid}")
        pause()

    def _view_positions(self):
        clear_screen()
        header("ALL POSITIONS", THEME_ADMIN)
        positions = self._position.get_all_positions()
        if not positions:
            print(); print_info("No positions found."); pause(); return
        print()
        table_header(
            f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}",
            THEME_ADMIN,
        )
        table_divider(70, THEME_ADMIN)
        for p in positions.values():
            badge = status_badge("Active", True) if p["is_active"] else status_badge("Inactive", False)
            print(f"  {p['id']:<5} {p['title']:<25} {p['level']:<12} {p['max_winners']:<8}"
                  f" {p['min_candidate_age']:<10} {badge}")
        print(f"\n  {DIM}Total Positions: {len(positions)}{RESET}")
        pause()

    def _update_position(self):
        clear_screen()
        header("UPDATE POSITION", THEME_ADMIN)
        positions = self._position.get_all_positions()
        if not positions:
            print(); print_info("No positions found."); pause(); return
        print()
        for p in positions.values():
            print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
        try:
            pid = int(prompt("\nEnter Position ID to update: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        p = self._position.get_position_by_id(pid)
        if not p:
            print_error("Position not found."); pause(); return

        print(f"\n  {BOLD}Updating: {p['title']}{RESET}")
        print_info("Press Enter to keep current value\n")
        updates = {
            "title":       prompt(f"Title [{p['title']}]: "),
            "description": prompt(f"Description [{p['description'][:50]}]: "),
            "level":       prompt(f"Level [{p['level']}]: "),
        }
        seats_raw = prompt(f"Seats [{p['max_winners']}]: ")
        if seats_raw:
            try:
                updates["max_winners"] = int(seats_raw)
            except ValueError:
                print_warning("Keeping old value.")
        self._position.update_position(pid, updates, self._user["username"])
        print(); print_success("Position updated!")
        pause()

    def _delete_position(self):
        clear_screen()
        header("DELETE POSITION", THEME_ADMIN)
        positions = self._position.get_all_positions()
        if not positions:
            print(); print_info("No positions found."); pause(); return
        print()
        for p in positions.values():
            print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
        try:
            pid = int(prompt("\nEnter Position ID to delete: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        if not self._position.get_position_by_id(pid):
            print_error("Position not found."); pause(); return
        if prompt(f"Confirm deactivation of '{positions[pid]['title']}'? (yes/no): ").lower() == "yes":
            ok, result = self._position.deactivate_position(pid, self._user["username"])
            if ok:
                print(); print_success("Position deactivated.")
            else:
                print_error(result)
        pause()

    # ══════════════════════════════════════════════════════════════════════════
    # POLL SCREENS
    # ══════════════════════════════════════════════════════════════════════════

    def _create_poll(self):
        import datetime as _dt
        clear_screen()
        header("CREATE POLL / ELECTION", THEME_ADMIN)
        print()
        title        = prompt("Poll/Election Title: ")
        if not title: print_error("Title cannot be empty."); pause(); return
        description  = prompt("Description: ")
        election_type = prompt("Election Type (General/Primary/By-election/Referendum): ")
        start_date   = prompt("Start Date (YYYY-MM-DD): ")
        end_date     = prompt("End Date (YYYY-MM-DD): ")
        try:
            sd = _dt.datetime.strptime(start_date, "%Y-%m-%d")
            ed = _dt.datetime.strptime(end_date,   "%Y-%m-%d")
            if ed <= sd: print_error("End date must be after start date."); pause(); return
        except ValueError:
            print_error("Invalid date format."); pause(); return

        positions = self._position.get_all_positions()
        if not positions: print_error("No positions available. Create positions first."); pause(); return
        active_positions = {pid: p for pid, p in positions.items() if p["is_active"]}
        if not active_positions: print_error("No active positions."); pause(); return

        subheader("Available Positions", THEME_ADMIN_ACCENT)
        for p in active_positions.values():
            print(f"    {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}) - {p['max_winners']} seat(s){RESET}")
        try:
            selected_pids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
        except ValueError:
            print_error("Invalid input."); pause(); return

        poll_positions = []
        for spid in selected_pids:
            if spid not in active_positions:
                print_warning(f"Position ID {spid} not found or inactive. Skipping.")
                continue
            poll_positions.append({
                "position_id":    spid,
                "position_title": positions[spid]["title"],
                "candidate_ids":  [],
                "max_winners":    positions[spid]["max_winners"],
            })
        if not poll_positions: print_error("No valid positions selected."); pause(); return

        stations = self._station.get_all_stations()
        if not stations: print_error("No voting stations. Create stations first."); pause(); return
        active_stations = {sid: s for sid, s in stations.items() if s["is_active"]}
        subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
        for s in active_stations.values():
            print(f"    {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET}")

        if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            selected_station_ids = list(active_stations.keys())
        else:
            try:
                selected_station_ids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
            except ValueError:
                print_error("Invalid input."); pause(); return

        pid = self._poll.create_poll(
            title, description, election_type, start_date, end_date,
            poll_positions, selected_station_ids, self._user["username"],
        )
        print(); print_success(f"Poll '{title}' created! ID: {pid}")
        print_warning("Status: DRAFT - Assign candidates and then open the poll.")
        pause()

    def _view_all_polls(self):
        clear_screen()
        header("ALL POLLS / ELECTIONS", THEME_ADMIN)
        polls = self._poll.get_all_polls()
        if not polls:
            print(); print_info("No polls found."); pause(); return
        for poll in polls.values():
            sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
            for pos in poll["positions"]:
                cand_names = [self._store.candidates[ccid]["full_name"]
                              for ccid in pos["candidate_ids"] if ccid in self._store.candidates]
                cand_display = ", ".join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cand_display}")
        print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
        pause()

    def _update_poll(self):
        import datetime as _dt
        clear_screen()
        header("UPDATE POLL", THEME_ADMIN)
        polls = self._poll.get_all_polls()
        if not polls:
            print(); print_info("No polls found."); pause(); return
        print()
        for poll in polls.values():
            sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID to update: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        poll = self._poll.get_poll_by_id(pid)
        if not poll:
            print_error("Poll not found."); pause(); return

        print(f"\n  {BOLD}Updating: {poll['title']}{RESET}")
        print_info("Press Enter to keep current value\n")
        updates = {
            "title":         prompt(f"Title [{poll['title']}]: "),
            "description":   prompt(f"Description [{poll['description'][:50]}]: "),
            "election_type": prompt(f"Election Type [{poll['election_type']}]: "),
        }
        new_start = prompt(f"Start Date [{poll['start_date']}]: ")
        if new_start:
            try:
                _dt.datetime.strptime(new_start, "%Y-%m-%d")
                updates["start_date"] = new_start
            except ValueError:
                print_warning("Invalid date, keeping old value.")
        new_end = prompt(f"End Date [{poll['end_date']}]: ")
        if new_end:
            try:
                _dt.datetime.strptime(new_end, "%Y-%m-%d")
                updates["end_date"] = new_end
            except ValueError:
                print_warning("Invalid date, keeping old value.")

        ok, err = self._poll.update_poll(pid, updates, self._user["username"])
        if ok:
            print(); print_success("Poll updated!")
        else:
            print_error(err)
        pause()

    def _delete_poll(self):
        clear_screen()
        header("DELETE POLL", THEME_ADMIN)
        polls = self._poll.get_all_polls()
        if not polls:
            print(); print_info("No polls found."); pause(); return
        print()
        for poll in polls.values():
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID to delete: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        poll = self._poll.get_poll_by_id(pid)
        if not poll:
            print_error("Poll not found."); pause(); return
        if poll["total_votes_cast"] > 0:
            print_warning(f"This poll has {poll['total_votes_cast']} votes recorded.")
        if prompt(f"Confirm deletion of '{poll['title']}'? (yes/no): ").lower() == "yes":
            ok, result = self._poll.delete_poll(pid, self._user["username"])
            if ok:
                title, _ = result
                print(); print_success(f"Poll '{title}' deleted.")
            else:
                print_error(result)
        pause()

    def _open_close_poll(self):
        clear_screen()
        header("OPEN / CLOSE POLL", THEME_ADMIN)
        polls = self._poll.get_all_polls()
        if not polls:
            print(); print_info("No polls found."); pause(); return
        print()
        for poll in polls.values():
            sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']}  {sc}{BOLD}{poll['status'].upper()}{RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        poll = self._poll.get_poll_by_id(pid)
        if not poll:
            print_error("Poll not found."); pause(); return

        if poll["status"] in ("draft", "closed"):
            action_label = "Open" if poll["status"] == "draft" else "Reopen"
            confirm_msg  = (f"Open poll '{poll['title']}'? Voting will begin. (yes/no): "
                            if poll["status"] == "draft"
                            else f"Reopen poll '{poll['title']}'? (yes/no): ")
            if poll["status"] == "closed":
                print_info("This poll is already closed.")
            if prompt(confirm_msg).lower() == "yes":
                ok, msg = self._poll.set_poll_status(pid, "open", self._user["username"])
                if ok:
                    print(); print_success(msg)
                else:
                    print_error(msg)
        elif poll["status"] == "open":
            if prompt(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): ").lower() == "yes":
                ok, msg = self._poll.set_poll_status(pid, "closed", self._user["username"])
                print(); print_success(msg) if ok else print_error(msg)
        pause()

    def _assign_candidates_to_poll(self):
        clear_screen()
        header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
        polls      = self._poll.get_all_polls()
        candidates = self._candidate.get_all_candidates()
        if not polls:     print(); print_info("No polls found.");     pause(); return
        if not candidates: print(); print_info("No candidates found."); pause(); return
        print()
        for poll in polls.values():
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        poll = self._poll.get_poll_by_id(pid)
        if not poll:
            print_error("Poll not found."); pause(); return
        if poll["status"] == "open":
            print_error("Cannot modify candidates of an open poll."); pause(); return

        for i, pos in enumerate(poll["positions"]):
            subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
            current_cands = [
                f"{ccid}: {candidates[ccid]['full_name']}"
                for ccid in pos["candidate_ids"] if ccid in candidates
            ]
            if current_cands:
                print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
            else:
                print_info("No candidates assigned yet.")

            pos_data = self._position.get_position_by_id(pos["position_id"]) or {}
            min_age  = pos_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
            eligible = {cid: c for cid, c in candidates.items()
                        if c["is_active"] and c["is_approved"] and c["age"] >= min_age}
            if not eligible:
                print_info("No eligible candidates found."); continue

            subheader("Available Candidates", THEME_ADMIN)
            for cid, c in eligible.items():
                marker = f" {GREEN}[ASSIGNED]{RESET}" if cid in pos["candidate_ids"] else ""
                print(f"    {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} "
                      f"{DIM}({c['party']}) - Age: {c['age']}, Edu: {c['education']}{RESET}{marker}")

            if prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
                try:
                    new_ids = [int(x.strip()) for x in prompt("Enter Candidate IDs (comma-separated): ").split(",")]
                    count, skipped = self._poll.assign_candidates(pid, i, new_ids, self._user["username"])
                    for s in skipped:
                        print_warning(f"Candidate {s} not eligible. Skipping.")
                    print_success(f"{count} candidate(s) assigned.")
                except ValueError:
                    print_error("Invalid input. Skipping this position.")
        pause()

    # ══════════════════════════════════════════════════════════════════════════
    # VOTER SCREENS
    # ══════════════════════════════════════════════════════════════════════════

    def _view_all_voters(self):
        clear_screen()
        header("ALL REGISTERED VOTERS", THEME_ADMIN)
        voters = self._voter.get_all_voters()
        if not voters:
            print(); print_info("No voters registered."); pause(); return
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}",
            THEME_ADMIN,
        )
        table_divider(70, THEME_ADMIN)
        for v in voters.values():
            verified = status_badge("Yes", True) if v["is_verified"] else status_badge("No", False)
            active   = status_badge("Yes", True) if v["is_active"]   else status_badge("No", False)
            print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15}"
                  f" {v['station_id']:<6} {verified:<19} {active}")
        verified_count   = sum(1 for v in voters.values() if v["is_verified"])
        unverified_count = sum(1 for v in voters.values() if not v["is_verified"])
        print(f"\n  {DIM}Total: {len(voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}{RESET}")
        pause()

    def _verify_voter(self):
        clear_screen()
        header("VERIFY VOTER", THEME_ADMIN)
        unverified = self._voter.get_unverified_voters()
        if not unverified:
            print(); print_info("No unverified voters."); pause(); return
        subheader("Unverified Voters", THEME_ADMIN_ACCENT)
        for v in unverified.values():
            print(f"  {THEME_ADMIN}{v['id']}.{RESET} {v['full_name']} "
                  f"{DIM}│ NID: {v['national_id']} │ Card: {v['voter_card_number']}{RESET}")
        print()
        menu_item(1, "Verify a single voter",     THEME_ADMIN)
        menu_item(2, "Verify all pending voters", THEME_ADMIN)
        choice = prompt("\nChoice: ")
        if choice == "1":
            try:
                vid = int(prompt("Enter Voter ID: "))
            except ValueError:
                print_error("Invalid input."); pause(); return
            ok, result = self._voter.verify_voter(vid, self._user["username"])
            if ok:
                print(); print_success(f"Voter '{result}' verified!")
            else:
                print_error(result) if result != "Already verified." else print_info(result)
        elif choice == "2":
            count = self._voter.verify_all_pending(self._user["username"])
            print(); print_success(f"{count} voters verified!")
        pause()

    def _deactivate_voter(self):
        clear_screen()
        header("DEACTIVATE VOTER", THEME_ADMIN)
        if not self._voter.get_all_voters():
            print(); print_info("No voters found."); pause(); return
        print()
        try:
            vid = int(prompt("Enter Voter ID to deactivate: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        v = self._voter.get_voter_by_id(vid)
        if not v:
            print_error("Voter not found."); pause(); return
        if prompt(f"Deactivate '{v['full_name']}'? (yes/no): ").lower() == "yes":
            ok, result = self._voter.deactivate_voter(vid, self._user["username"])
            if ok:
                print(); print_success("Voter deactivated.")
            else:
                print_info(result)
        pause()

    def _search_voters(self):
        clear_screen()
        header("SEARCH VOTERS", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name",              THEME_ADMIN)
        menu_item(2, "Voter Card Number", THEME_ADMIN)
        menu_item(3, "National ID",       THEME_ADMIN)
        menu_item(4, "Station",           THEME_ADMIN)
        choice = prompt("\nChoice: ")

        results = []
        if choice == "1":
            term = prompt("Name: ")
            results = self._voter.search_by_name(term)
        elif choice == "2":
            term = prompt("Card Number: ")
            results = self._voter.search_by_card_number(term)
        elif choice == "3":
            term = prompt("National ID: ")
            results = self._voter.search_by_national_id(term)
        elif choice == "4":
            try:
                sid = int(prompt("Station ID: "))
                results = self._voter.search_by_station(sid)
            except ValueError:
                print_error("Invalid input."); pause(); return
        else:
            print_error("Invalid choice."); pause(); return

        if not results:
            print(); print_info("No voters found.")
        else:
            print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
            for v in results:
                verified = status_badge("Verified", True) if v["is_verified"] else status_badge("Unverified", False)
                print(f"  {THEME_ADMIN}ID:{RESET} {v['id']}  {DIM}│{RESET}  {v['full_name']}"
                      f"  {DIM}│  Card:{RESET} {v['voter_card_number']}  {DIM}│{RESET}  {verified}")
        pause()

    # ══════════════════════════════════════════════════════════════════════════
    # ADMIN MANAGEMENT SCREENS
    # ══════════════════════════════════════════════════════════════════════════

    def _create_admin(self):
        clear_screen()
        header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
        if self._user["role"] != "super_admin":
            print(); print_error("Only super admins can create admin accounts."); pause(); return
        print()
        username  = prompt("Username: ")
        full_name = prompt("Full Name: ")
        email     = prompt("Email: ")
        password  = masked_input("Password: ").strip()
        subheader("Available Roles", THEME_ADMIN_ACCENT)
        menu_item(1, f"super_admin {DIM}─ Full access{RESET}",                          THEME_ADMIN)
        menu_item(2, f"election_officer {DIM}─ Manage polls and candidates{RESET}",     THEME_ADMIN)
        menu_item(3, f"station_manager {DIM}─ Manage stations and verify voters{RESET}", THEME_ADMIN)
        menu_item(4, f"auditor {DIM}─ Read-only access{RESET}",                         THEME_ADMIN)
        role_choice = prompt("\nSelect role (1-4): ")
        role = ADMIN_ROLES.get(role_choice)
        if not role:
            print_error("Invalid role."); pause(); return

        ok, result = self._admin.create_admin(
            username, full_name, email, password, role, self._user["username"]
        )
        if ok:
            print(); print_success(f"Admin '{username}' created with role: {role}")
        else:
            print_error(result)
        pause()

    def _view_admins(self):
        clear_screen()
        header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
        print()
        table_header(
            f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}",
            THEME_ADMIN,
        )
        table_divider(78, THEME_ADMIN)
        for a in self._admin.get_all_admins().values():
            active = status_badge("Yes", True) if a["is_active"] else status_badge("No", False)
            print(f"  {a['id']:<5} {a['username']:<20} {a['full_name']:<25} {a['role']:<20} {active}")
        print(f"\n  {DIM}Total Admins: {len(self._admin.get_all_admins())}{RESET}")
        pause()

    def _deactivate_admin(self):
        clear_screen()
        header("DEACTIVATE ADMIN", THEME_ADMIN)
        if self._user["role"] != "super_admin":
            print(); print_error("Only super admins can deactivate admins."); pause(); return
        print()
        for a in self._admin.get_all_admins().values():
            badge = status_badge("Active", True) if a["is_active"] else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{a['id']}.{RESET} {a['username']} {DIM}({a['role']}){RESET} {badge}")
        try:
            aid = int(prompt("\nEnter Admin ID to deactivate: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        if prompt(f"Deactivate '{self._store.admins.get(aid, {}).get('username', '?')}'? (yes/no): ").lower() == "yes":
            ok, result = self._admin.deactivate_admin(aid, self._user["id"], self._user["username"])
            if ok:
                print(); print_success("Admin deactivated.")
            else:
                print_error(result)
        pause()

    # ══════════════════════════════════════════════════════════════════════════
    # RESULTS & REPORTS SCREENS
    # ══════════════════════════════════════════════════════════════════════════

    def _view_poll_results(self):
        clear_screen()
        header("POLL RESULTS", THEME_ADMIN)
        polls = self._poll.get_all_polls()
        if not polls:
            print(); print_info("No polls found."); pause(); return
        print()
        for poll in polls.values():
            sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        poll = self._poll.get_poll_by_id(pid)
        if not poll:
            print_error("Poll not found."); pause(); return

        print()
        header(f"RESULTS: {poll['title']}", THEME_ADMIN)
        sc = GREEN if poll["status"] == "open" else RED
        print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}  {DIM}│  Votes:{RESET} {BOLD}{poll['total_votes_cast']}{RESET}")
        total_eligible, turnout = self._poll.calculate_turnout(pid)
        tc = GREEN if turnout > 50 else (YELLOW if turnout > 25 else RED)
        print(f"  {DIM}Eligible:{RESET} {total_eligible}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")

        for pos in poll["positions"]:
            subheader(f"{pos['position_title']} (Seats: {pos['max_winners']})", THEME_ADMIN_ACCENT)
            data = self._poll.calculate_position_results(pid, pos["position_id"])
            vote_counts   = data["vote_counts"]
            abstain_count = data["abstain_count"]
            total_pos     = data["total_pos"]

            for rank, (cid, count) in enumerate(
                sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1
            ):
                cand = self._store.candidates.get(cid, {})
                pct  = (count / total_pos * 100) if total_pos > 0 else 0
                bl   = int(pct / 2)
                bar  = f"{THEME_ADMIN}{'█' * bl}{GRAY}{'░' * (50 - bl)}{RESET}"
                winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= pos["max_winners"] else ""
                print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
            if abstain_count > 0:
                pct = (abstain_count / total_pos * 100) if total_pos > 0 else 0
                print(f"    {GRAY}Abstained: {abstain_count} ({pct:.1f}%){RESET}")
            if not vote_counts:
                print_info("    No votes recorded for this position.")
        pause()

    def _view_detailed_statistics(self):
        clear_screen()
        header("DETAILED STATISTICS", THEME_ADMIN)
        stats = self._vote.get_statistics()

        subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
        print(f"  {THEME_ADMIN}Candidates:{RESET}  {stats['total_candidates']} {DIM}(Active: {stats['active_candidates']}){RESET}")
        print(f"  {THEME_ADMIN}Voters:{RESET}      {stats['total_voters']} {DIM}(Verified: {stats['verified_voters']}, Active: {stats['active_voters']}){RESET}")
        print(f"  {THEME_ADMIN}Stations:{RESET}    {stats['total_stations']} {DIM}(Active: {stats['active_stations']}){RESET}")
        print(f"  {THEME_ADMIN}Polls:{RESET}       {stats['total_polls']} "
              f"{DIM}({GREEN}Open: {stats['open_polls']}{RESET}{DIM}, "
              f"{RED}Closed: {stats['closed_polls']}{RESET}{DIM}, "
              f"{YELLOW}Draft: {stats['draft_polls']}{RESET}{DIM}){RESET}")
        print(f"  {THEME_ADMIN}Total Votes:{RESET} {stats['total_votes']}")

        subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
        tv = stats["total_voters"]
        for g, count in stats["gender_counts"].items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {g}: {count} ({pct:.1f}%)")
        print(f"  {BOLD}Age Distribution:{RESET}")
        for group, count in stats["age_groups"].items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) {THEME_ADMIN}{'█' * int(pct / 2)}{RESET}")

        subheader("STATION LOAD", THEME_ADMIN_ACCENT)
        for sid_str, sl in stats["station_load"].items():
            lp = sl["load_pct"]
            lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
            st = f"{RED}{BOLD}OVERLOADED{RESET}" if lp > 100 else f"{GREEN}OK{RESET}"
            print(f"    {sl['name']}: {sl['voters']}/{sl['capacity']} {lc}({lp:.0f}%){RESET} {st}")

        subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
        for party, count in sorted(stats["party_counts"].items(), key=lambda x: x[1], reverse=True):
            print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")

        subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
        for edu, count in stats["edu_counts"].items():
            print(f"    {edu}: {BOLD}{count}{RESET}")
        pause()

    def _station_wise_results(self):
        clear_screen()
        header("STATION-WISE RESULTS", THEME_ADMIN)
        polls = self._poll.get_all_polls()
        if not polls:
            print(); print_info("No polls found."); pause(); return
        print()
        for poll in polls.values():
            sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        poll = self._poll.get_poll_by_id(pid)
        if not poll:
            print_error("Poll not found."); pause(); return

        print()
        header(f"STATION RESULTS: {poll['title']}", THEME_ADMIN)
        for sid in poll["station_ids"]:
            station = self._store.voting_stations.get(sid)
            if not station:
                continue
            subheader(f"{station['name']}  ({station['location']})", BRIGHT_WHITE)
            data = self._poll.calculate_station_results(pid, sid)
            tc   = GREEN if data["turnout"] > 50 else (YELLOW if data["turnout"] > 25 else RED)
            print(f"  {DIM}Registered:{RESET} {data['registered']}  {DIM}│  Voted:{RESET} {data['voted_count']}"
                  f"  {DIM}│  Turnout:{RESET} {tc}{BOLD}{data['turnout']:.1f}%{RESET}")
            for pos in poll["positions"]:
                print(f"    {THEME_ADMIN_ACCENT}▸ {pos['position_title']}:{RESET}")
                pv = [v for v in data["station_votes"] if v["position_id"] == pos["position_id"]]
                vc = {}; ac = 0
                for v in pv:
                    if v["abstained"]:
                        ac += 1
                    else:
                        vc[v["candidate_id"]] = vc.get(v["candidate_id"], 0) + 1
                total = sum(vc.values()) + ac
                for cid, count in sorted(vc.items(), key=lambda x: x[1], reverse=True):
                    cand = self._store.candidates.get(cid, {})
                    pct  = (count / total * 100) if total > 0 else 0
                    print(f"      {cand.get('full_name', '?')} {DIM}({cand.get('party', '?')}){RESET}:"
                          f" {BOLD}{count}{RESET} ({pct:.1f}%)")
                if ac > 0:
                    print(f"      {GRAY}Abstained: {ac} ({(ac/total*100) if total>0 else 0:.1f}%){RESET}")
        pause()

    def _view_audit_log(self):
        clear_screen()
        header("AUDIT LOG", THEME_ADMIN)
        audit_log = self._store.audit_log
        if not audit_log:
            print(); print_info("No audit records."); pause(); return

        print(f"\n  {DIM}Total Records: {len(audit_log)}{RESET}")
        subheader("Filter", THEME_ADMIN_ACCENT)
        menu_item(1, "Last 20 entries",       THEME_ADMIN)
        menu_item(2, "All entries",            THEME_ADMIN)
        menu_item(3, "Filter by action type", THEME_ADMIN)
        menu_item(4, "Filter by user",        THEME_ADMIN)
        choice = prompt("\nChoice: ")

        entries = audit_log
        if choice == "1":
            entries = audit_log[-20:]
        elif choice == "3":
            action_types = list(set(e["action"] for e in audit_log))
            for i, at in enumerate(action_types, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
            try:
                at_choice = int(prompt("Select action type: "))
                entries = [e for e in audit_log if e["action"] == action_types[at_choice - 1]]
            except (ValueError, IndexError):
                print_error("Invalid choice."); pause(); return
        elif choice == "4":
            uf = prompt("Enter username/card number: ")
            entries = [e for e in audit_log if uf.lower() in e["user"].lower()]

        print()
        table_header(f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}", THEME_ADMIN)
        table_divider(100, THEME_ADMIN)
        for entry in entries:
            ac = (GREEN if "CREATE" in entry["action"] or entry["action"] == "LOGIN"
                  else RED if "DELETE" in entry["action"] or "DEACTIVATE" in entry["action"]
                  else YELLOW if "UPDATE" in entry["action"] else RESET)
            print(f"  {DIM}{entry['timestamp'][:19]}{RESET}  {ac}{entry['action']:<25}{RESET}"
                  f" {entry['user']:<20} {DIM}{entry['details'][:50]}{RESET}")
        pause()
