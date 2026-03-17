"""
admin_dashboard.py - Full admin dashboard matching the original e_voting_console_app.py.
All 32 menu options with every CRUD operation. Data access via DatabaseEngine.
"""
import datetime
from ui import (clear_screen, header, subheader, menu_item, prompt, masked_input,
                pause, error, success, warning, info, status_badge,
                table_header, table_divider)
from colors import *
from security import hash_password

MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75
REQUIRED_EDUCATION_LEVELS = ["Bachelor's Degree", "Master's Degree", "PhD", "Doctorate"]


def admin_dashboard(current_user):
    while True:
        clear_screen()
        header("ADMIN DASHBOARD", THEME_ADMIN)
        print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{current_user['full_name']}{RESET}  {DIM}│  Role: {current_user['role']}{RESET}")

        subheader("Candidate Management", THEME_ADMIN_ACCENT)
        menu_item(1, "Create Candidate", THEME_ADMIN)
        menu_item(2, "View All Candidates", THEME_ADMIN)
        menu_item(3, "Update Candidate", THEME_ADMIN)
        menu_item(4, "Delete Candidate", THEME_ADMIN)
        menu_item(5, "Search Candidates", THEME_ADMIN)

        subheader("Voting Station Management", THEME_ADMIN_ACCENT)
        menu_item(6, "Create Voting Station", THEME_ADMIN)
        menu_item(7, "View All Stations", THEME_ADMIN)
        menu_item(8, "Update Station", THEME_ADMIN)
        menu_item(9, "Delete Station", THEME_ADMIN)

        subheader("Polls & Positions", THEME_ADMIN_ACCENT)
        menu_item(10, "Create Position", THEME_ADMIN)
        menu_item(11, "View Positions", THEME_ADMIN)
        menu_item(12, "Update Position", THEME_ADMIN)
        menu_item(13, "Delete Position", THEME_ADMIN)
        menu_item(14, "Create Poll", THEME_ADMIN)
        menu_item(15, "View All Polls", THEME_ADMIN)
        menu_item(16, "Update Poll", THEME_ADMIN)
        menu_item(17, "Delete Poll", THEME_ADMIN)
        menu_item(18, "Open/Close Poll", THEME_ADMIN)
        menu_item(19, "Assign Candidates to Poll", THEME_ADMIN)

        subheader("Voter Management", THEME_ADMIN_ACCENT)
        menu_item(20, "View All Voters", THEME_ADMIN)
        menu_item(21, "Verify Voter", THEME_ADMIN)
        menu_item(22, "Deactivate Voter", THEME_ADMIN)
        menu_item(23, "Search Voters", THEME_ADMIN)

        subheader("Admin Management", THEME_ADMIN_ACCENT)
        menu_item(24, "Create Admin Account", THEME_ADMIN)
        menu_item(25, "View Admins", THEME_ADMIN)
        menu_item(26, "Deactivate Admin", THEME_ADMIN)

        subheader("Results & Reports", THEME_ADMIN_ACCENT)
        menu_item(27, "View Poll Results", THEME_ADMIN)
        menu_item(28, "View Detailed Statistics", THEME_ADMIN)
        menu_item(29, "View Audit Log", THEME_ADMIN)
        menu_item(30, "Station-wise Results", THEME_ADMIN)

        subheader("System", THEME_ADMIN_ACCENT)
        menu_item(31, "Save Data", THEME_ADMIN)
        menu_item(32, "Logout", THEME_ADMIN)
        print()
        choice = prompt("Enter choice: ")

        if choice == "1": create_candidate(current_user)
        elif choice == "2": view_all_candidates()
        elif choice == "3": update_candidate(current_user)
        elif choice == "4": delete_candidate(current_user)
        elif choice == "5": search_candidates()
        elif choice == "6": create_voting_station(current_user)
        elif choice == "7": view_all_stations()
        elif choice == "8": update_station(current_user)
        elif choice == "9": delete_station(current_user)
        elif choice == "10": create_position(current_user)
        elif choice == "11": view_positions()
        elif choice == "12": update_position(current_user)
        elif choice == "13": delete_position(current_user)
        elif choice == "14": create_poll(current_user)
        elif choice == "15": view_all_polls()
        elif choice == "16": update_poll(current_user)
        elif choice == "17": delete_poll(current_user)
        elif choice == "18": open_close_poll(current_user)
        elif choice == "19": assign_candidates_to_poll(current_user)
        elif choice == "20": view_all_voters()
        elif choice == "21": verify_voter(current_user)
        elif choice == "22": deactivate_voter(current_user)
        elif choice == "23": search_voters()
        elif choice == "24": create_admin(current_user)
        elif choice == "25": view_admins()
        elif choice == "26": deactivate_admin(current_user)
        elif choice == "27":
            from stats_results import view_poll_results; view_poll_results()
        elif choice == "28":
            from stats_results import view_detailed_statistics; view_detailed_statistics()
        elif choice == "29":
            from stats_results import view_audit_log; view_audit_log()
        elif choice == "30":
            from stats_results import station_wise_results; station_wise_results()
        elif choice == "31": pause()
        elif choice == "32":
            from Backend.audits import LogAuditEntry
            LogAuditEntry().execute("LOGOUT", current_user["username"], "Admin logged out")
            break
        else: error("Invalid choice."); pause()


# ── Candidate Management ──────────────────────────────────────────────────────

def create_candidate(current_user):
    from Backend.candidate_management.CreateCandidateService import CandidateService
    CandidateService.create_candidate()

def view_all_candidates():
    from Backend.candidate_management.CandidateViewService import CandidateViewService
    CandidateViewService.view_all()

def update_candidate(current_user):
    from Backend.candidate_management.CandidateUpdateService import CandidateUpdateService
    CandidateUpdateService.update_candidate()

def delete_candidate(current_user):
    from Backend.candidate_management.DeleteCandidateService import DeleteCandidate
    DeleteCandidate().execute()

def search_candidates():
    from Backend.candidate_management.SearchCandidatesService import SearchCandidates
    SearchCandidates().execute()


# ── Station Management ────────────────────────────────────────────────────────

def create_voting_station(current_user):
    clear_screen()
    header("CREATE VOTING STATION", THEME_ADMIN)
    print()
    name = prompt("Station Name: ")
    if not name: error("Name cannot be empty."); pause(); return
    location = prompt("Location/Address: ")
    if not location: error("Location cannot be empty."); pause(); return
    region = prompt("Region/District: ")
    try:
        capacity = int(prompt("Voter Capacity: "))
        if capacity <= 0: error("Capacity must be positive."); pause(); return
    except ValueError: error("Invalid capacity."); pause(); return
    supervisor = prompt("Station Supervisor Name: ")
    contact = prompt("Contact Phone: ")
    opening_time = prompt("Opening Time (e.g. 08:00): ")
    closing_time = prompt("Closing Time (e.g. 17:00): ")
    
    from Backend.station_management import CreateStation
    from Backend.audits import LogAuditEntry
    
    try:
        new_station = CreateStation(current_user["username"]).execute(
            name=name, location=location, region=region, capacity=capacity,
            supervisor=supervisor, contact_phone=contact,
            opening_time=opening_time, closing_time=closing_time
        )
        sid = new_station["id"]
        LogAuditEntry().execute("CREATE_STATION", current_user["username"], f"Created station: {name} (ID: {sid})")
        print(); success(f"Voting Station '{name}' created! ID: {sid}")
    except ValueError as e:
        error(str(e))
    except Exception as e:
        error(str(e))
    pause()


def view_all_stations():
    clear_screen()
    header("ALL VOTING STATIONS", THEME_ADMIN)
    
    from Backend.station_management import GetAllStations, CountRegisteredVoters
    from Backend.voters_management import GetAllVoters
    
    stations = GetAllStations().execute()
    voters = GetAllVoters().execute()
    
    if not stations: print(); info("No voting stations found."); pause(); return
    print()
    table_header(f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}", THEME_ADMIN)
    table_divider(96, THEME_ADMIN)
    
    counter = CountRegisteredVoters(voters)
    for s in stations:
        reg_count = counter.execute(s["id"])
        st = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
        print(f"  {s['id']:<5} {s['name']:<25} {s['location']:<25} {s['region']:<15} {s['capacity']:<8} {reg_count:<8} {st}")
    print(f"\n  {DIM}Total Stations: {len(stations)}{RESET}")
    pause()


def update_station(current_user):
    clear_screen()
    header("UPDATE VOTING STATION", THEME_ADMIN)
    
    from Backend.station_management import GetAllStations, UpdateStation
    from Backend.audits import LogAuditEntry
    stations_list = GetAllStations().execute()
    stations = {s["id"]: s for s in stations_list}
    
    if not stations: print(); info("No stations found."); pause(); return
    print()
    for sid, s in stations.items():
        print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")
    try: sid = int(prompt("\nEnter Station ID to update: "))
    except ValueError: error("Invalid input."); pause(); return
    if sid not in stations: error("Station not found."); pause(); return
    s = stations[sid]
    print(f"\n  {BOLD}Updating: {s['name']}{RESET}")
    info("Press Enter to keep current value\n")
    changes = {}
    nn = prompt(f"Name [{s['name']}]: ");
    if nn: changes["name"] = nn
    nl = prompt(f"Location [{s['location']}]: ");
    if nl: changes["location"] = nl
    nr = prompt(f"Region [{s['region']}]: ");
    if nr: changes["region"] = nr
    nc = prompt(f"Capacity [{s['capacity']}]: ")
    if nc:
        try: changes["capacity"] = int(nc)
        except ValueError: warning("Invalid number, keeping old value.")
    ns = prompt(f"Supervisor [{s['supervisor']}]: ");
    if ns: changes["supervisor"] = ns
    nco = prompt(f"Contact [{s.get('contact_phone', '')}]: ");
    if nco: changes["contact_phone"] = nco
    
    if changes:
        try:
            UpdateStation().execute(sid, changes)
            LogAuditEntry().execute("UPDATE_STATION", current_user["username"], f"Updated station: {changes.get('name', s['name'])} (ID: {sid})")
            print(); success(f"Station '{changes.get('name', s['name'])}' updated successfully!")
        except Exception as e:
            error(str(e))
    pause()


def delete_station(current_user):
    clear_screen()
    header("DELETE VOTING STATION", THEME_ADMIN)
    
    from Backend.station_management import GetAllStations, DeactivateStation
    from Backend.voters_management import GetAllVoters
    from Backend.audits import LogAuditEntry
    stations_list = GetAllStations().execute()
    stations = {s["id"]: s for s in stations_list}
    voters = GetAllVoters().execute()
    
    if not stations: print(); info("No stations found."); pause(); return
    print()
    for sid, s in stations.items():
        st = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET} {st}")
    try: sid = int(prompt("\nEnter Station ID to delete: "))
    except ValueError: error("Invalid input."); pause(); return
    if sid not in stations: error("Station not found."); pause(); return
    
    if prompt(f"Confirm deactivation of '{stations[sid]['name']}'? (yes/no): ").lower() == "yes":
        try:
            DeactivateStation(voters).execute(sid, force=True)
            LogAuditEntry().execute("DELETE_STATION", current_user["username"], f"Deactivated station: {stations[sid]['name']}")
            print(); success(f"Station '{stations[sid]['name']}' deactivated.")
        except Exception as e:
            error(str(e))
    else: info("Cancelled.")
    pause()


# ── Position Management ───────────────────────────────────────────────────────

def create_position(current_user):
    clear_screen()
    header("CREATE POSITION", THEME_ADMIN)
    print()
    title = prompt("Position Title (e.g. President, Governor, Senator): ")
    if not title: error("Title cannot be empty."); pause(); return
    description = prompt("Description: ")
    level = prompt("Level (National/Regional/Local): ")
    if level.lower() not in ["national", "regional", "local"]: error("Invalid level."); pause(); return
    try:
        max_winners = int(prompt("Number of winners/seats: "))
        if max_winners <= 0: error("Must be at least 1."); pause(); return
    except ValueError: error("Invalid number."); pause(); return
    min_cand_age = prompt(f"Minimum candidate age [{MIN_CANDIDATE_AGE}]: ")
    min_cand_age = int(min_cand_age) if min_cand_age.isdigit() else MIN_CANDIDATE_AGE
    
    from Backend.position_management import CreatePosition
    from Backend.audits import LogAuditEntry
    
    try:
        new_pos = CreatePosition(current_user["username"]).execute(title, description, level, max_winners, min_cand_age)
        pid = new_pos["id"]
        LogAuditEntry().execute("CREATE_POSITION", current_user["username"], f"Created position: {title} (ID: {pid})")
        print(); success(f"Position '{title}' created! ID: {pid}")
    except ValueError as e:
        error(str(e))
    except Exception as e:
        error(str(e))
    pause()


def view_positions():
    clear_screen()
    header("ALL POSITIONS", THEME_ADMIN)
    
    from Backend.position_management import GetAllPositions
    positions = GetAllPositions().execute()
    
    if not positions: print(); info("No positions found."); pause(); return
    print()
    table_header(f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}", THEME_ADMIN)
    table_divider(70, THEME_ADMIN)
    for p in positions:
        s = status_badge("Active", True) if p["is_active"] else status_badge("Inactive", False)
        print(f"  {p['id']:<5} {p['title']:<25} {p['level']:<12} {p['max_winners']:<8} {p['min_candidate_age']:<10} {s}")
    print(f"\n  {DIM}Total Positions: {len(positions)}{RESET}")
    pause()


def update_position(current_user):
    clear_screen()
    header("UPDATE POSITION", THEME_ADMIN)
    
    from Backend.position_management import GetAllPositions, UpdatePosition
    from Backend.audits import LogAuditEntry
    positions_list = GetAllPositions().execute()
    positions = {p["id"]: p for p in positions_list}
    
    if not positions: print(); info("No positions found."); pause(); return
    print()
    for pid, p in positions.items():
        print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
    try: pid = int(prompt("\nEnter Position ID to update: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in positions: error("Position not found."); pause(); return
    p = positions[pid]
    print(f"\n  {BOLD}Updating: {p['title']}{RESET}")
    info("Press Enter to keep current value\n")
    changes = {}
    nt = prompt(f"Title [{p['title']}]: ")
    if nt: changes["title"] = nt
    nd = prompt(f"Description [{p['description'][:50]}]: ")
    if nd: changes["description"] = nd
    nl = prompt(f"Level [{p['level']}]: ")
    if nl and nl.lower() in ["national", "regional", "local"]: changes["level"] = nl.capitalize()
    ns = prompt(f"Seats [{p['max_winners']}]: ")
    if ns:
        try: changes["max_winners"] = int(ns)
        except ValueError: warning("Keeping old value.")
        
    if changes:
        try:
            UpdatePosition().execute(pid, changes)
            LogAuditEntry().execute("UPDATE_POSITION", current_user["username"], f"Updated position: {changes.get('title', p['title'])}")
            print(); success("Position updated!")
        except Exception as e:
            error(str(e))
    pause()


def delete_position(current_user):
    clear_screen()
    header("DELETE POSITION", THEME_ADMIN)
    
    from Backend.position_management import GetAllPositions, DeactivatePosition
    from Backend.polls_management import GetAllPolls
    from Backend.audits import LogAuditEntry
    positions_list = GetAllPositions().execute()
    positions = {p["id"]: p for p in positions_list}
    polls_list = GetAllPolls().execute()
    
    if not positions: print(); info("No positions found."); pause(); return
    print()
    for pid, p in positions.items():
        print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
    try: pid = int(prompt("\nEnter Position ID to delete: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in positions: error("Position not found."); pause(); return
    
    if prompt(f"Confirm deactivation of '{positions[pid]['title']}'? (yes/no): ").lower() == "yes":
        try:
            DeactivatePosition(polls_list).execute(pid)
            LogAuditEntry().execute("DELETE_POSITION", current_user["username"], f"Deactivated position: {positions[pid]['title']}")
            print(); success("Position deactivated.")
        except Exception as e:
            error(str(e))
    pause()


# ── Poll Management ───────────────────────────────────────────────────────────

def create_poll(current_user):
    clear_screen()
    header("CREATE POLL / ELECTION", THEME_ADMIN)
    print()
    title = prompt("Poll/Election Title: ")
    if not title: error("Title cannot be empty."); pause(); return
    description = prompt("Description: ")
    election_type = prompt("Election Type (General/Primary/By-election/Referendum): ")
    start_date = prompt("Start Date (YYYY-MM-DD): ")
    end_date = prompt("End Date (YYYY-MM-DD): ")
    try:
        sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        if ed <= sd: error("End date must be after start date."); pause(); return
    except ValueError: error("Invalid date format."); pause(); return
    
    from Backend.position_management import GetAllPositions
    from Backend.station_management import GetAllStations
    from Backend.polls_management import CreatePoll
    from Backend.audits import LogAuditEntry
    
    positions_list = GetAllPositions().execute()
    positions = {p["id"]: p for p in positions_list}
    if not positions: error("No positions available. Create positions first."); pause(); return
    
    subheader("Available Positions", THEME_ADMIN_ACCENT)
    active_pos = {pid: p for pid, p in positions.items() if p["is_active"]}
    if not active_pos: error("No active positions."); pause(); return
    for pid, p in active_pos.items():
        print(f"    {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}) - {p['max_winners']} seat(s){RESET}")
        
    try: sel_pos_ids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
    except ValueError: error("Invalid input."); pause(); return
    poll_positions = []
    for spid in sel_pos_ids:
        if spid not in active_pos: warning(f"Position ID {spid} not found or inactive. Skipping."); continue
        poll_positions.append({"position_id": spid, "position_title": positions[spid]["title"], "candidate_ids": [], "max_winners": positions[spid]["max_winners"]})
    if not poll_positions: error("No valid positions selected."); pause(); return
    
    stations_list = GetAllStations().execute()
    stations = {s["id"]: s for s in stations_list}
    if not stations: error("No voting stations. Create stations first."); pause(); return
    
    subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
    active_st = {sid: s for sid, s in stations.items() if s["is_active"]}
    for sid, s in active_st.items():
        print(f"    {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET}")
    if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
        sel_st_ids = list(active_st.keys())
    else:
        try: sel_st_ids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
        except ValueError: error("Invalid input."); pause(); return
        
    try:
        new_poll = CreatePoll(current_user["username"]).execute(
            title=title, description=description, election_type=election_type,
            start_date=start_date, end_date=end_date, positions=poll_positions, station_ids=sel_st_ids
        )
        poll_id = new_poll["id"]
        LogAuditEntry().execute("POLL_CREATED", current_user["username"], f"Created poll: {title} (ID: {poll_id})")
        print(); success(f"Poll '{title}' created! ID: {poll_id}")
        warning("Status: DRAFT - Assign candidates and then open the poll.")
    except Exception as e:
        error(str(e))
    pause()


def view_all_polls():
    clear_screen()
    header("ALL POLLS / ELECTIONS", THEME_ADMIN)
    
    from Backend.polls_management import GetAllPolls
    from frontend_service import GetAllCandidatesService
    polls_list = GetAllPolls().execute()
    polls = {p["id"]: p for p in polls_list}
    
    candidates_list = GetAllCandidatesService().execute()
    candidates = {c["id"]: c for c in candidates_list}
    
    if not polls: print(); info("No polls found."); pause(); return
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{RESET}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}")
        print(f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
        for pos in poll["positions"]:
            cand_names = [candidates[ccid]["full_name"] for ccid in pos["candidate_ids"] if ccid in candidates]
            cand_display = ', '.join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
            print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cand_display}")
    print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
    pause()


def update_poll(current_user):
    clear_screen()
    header("UPDATE POLL", THEME_ADMIN)
    
    from Backend.polls_management import GetAllPolls, UpdatePoll
    from Backend.audits import LogAuditEntry
    
    polls_list = GetAllPolls().execute()
    polls = {p["id"]: p for p in polls_list}
    
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
    try: pid = int(prompt("\nEnter Poll ID to update: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    if poll["status"] == "open": error("Cannot update an open poll. Close it first."); pause(); return
    if poll["status"] == "closed" and poll["total_votes_cast"] > 0: error("Cannot update a poll with votes."); pause(); return
    print(f"\n  {BOLD}Updating: {poll['title']}{RESET}")
    info("Press Enter to keep current value\n")
    changes = {}
    nt = prompt(f"Title [{poll['title']}]: ")
    if nt: changes["title"] = nt
    nd = prompt(f"Description [{poll['description'][:50]}]: ")
    if nd: changes["description"] = nd
    nty = prompt(f"Election Type [{poll['election_type']}]: ")
    if nty: changes["election_type"] = nty
    ns = prompt(f"Start Date [{poll['start_date']}]: ")
    if ns:
        try: datetime.datetime.strptime(ns, "%Y-%m-%d"); changes["start_date"] = ns
        except ValueError: warning("Invalid date, keeping old value.")
    ne = prompt(f"End Date [{poll['end_date']}]: ")
    if ne:
        try: datetime.datetime.strptime(ne, "%Y-%m-%d"); changes["end_date"] = ne
        except ValueError: warning("Invalid date, keeping old value.")
        
    if changes:
        try:
            UpdatePoll().execute(pid, changes)
            LogAuditEntry().execute("POLL_UPDATED", current_user["username"], f"Updated poll: {changes.get('title', poll['title'])}")
            print(); success("Poll updated!")
        except Exception as e:
            error(str(e))
    pause()


def delete_poll(current_user):
    clear_screen()
    header("DELETE POLL", THEME_ADMIN)
    
    from Backend.polls_management import GetAllPolls, DeletePoll
    from Backend.audits import LogAuditEntry
    polls_list = GetAllPolls().execute()
    polls = {p["id"]: p for p in polls_list}
    
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
    try: pid = int(prompt("\nEnter Poll ID to delete: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    if polls[pid]["status"] == "open": error("Cannot delete an open poll. Close it first."); pause(); return
    if polls[pid]["total_votes_cast"] > 0: warning(f"This poll has {polls[pid]['total_votes_cast']} votes recorded.")
    if prompt(f"Confirm deletion of '{polls[pid]['title']}'? (yes/no): ").lower() == "yes":
        deleted_title = polls[pid]["title"]
        try:
            DeletePoll().execute(pid)
            LogAuditEntry().execute("POLL_DELETED", current_user["username"], f"Deleted poll: {deleted_title}")
            print(); success(f"Poll '{deleted_title}' deleted.")
        except Exception as e:
            error(str(e))
    pause()


def open_close_poll(current_user):
    clear_screen()
    header("OPEN / CLOSE POLL", THEME_ADMIN)
    
    from Backend.polls_management import GetAllPolls, OpenPoll, ClosePoll
    from Backend.audits import LogAuditEntry
    polls_list = GetAllPolls().execute()
    polls = {p["id"]: p for p in polls_list}
    
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']}  {sc}{BOLD}{poll['status'].upper()}{RESET}")
    try: pid = int(prompt("\nEnter Poll ID: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    
    try:
        if poll["status"] == "draft":
            if prompt(f"Open poll '{poll['title']}'? Voting will begin. (yes/no): ").lower() == "yes":
                OpenPoll().execute(pid)
                LogAuditEntry().execute("POLL_OPENED", current_user["username"], f"Opened poll: {poll['title']}")
                print(); success(f"Poll '{poll['title']}' is now OPEN for voting!")
        elif poll["status"] == "open":
            if prompt(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): ").lower() == "yes":
                ClosePoll().execute(pid)
                LogAuditEntry().execute("POLL_CLOSED", current_user["username"], f"Closed poll: {poll['title']}")
                print(); success(f"Poll '{poll['title']}' is now CLOSED.")
        elif poll["status"] == "closed":
            info("This poll is already closed.")
            if prompt("Reopen it? (yes/no): ").lower() == "yes":
                from Backend.polls_management import UpdatePoll
                UpdatePoll().execute(pid, {"status": "open"})
                LogAuditEntry().execute("POLL_OPENED", current_user["username"], f"Reopened poll: {poll['title']}")
                print(); success("Poll reopened!")
    except Exception as e:
        error(str(e))
    pause()


def assign_candidates_to_poll(current_user):
    clear_screen()
    header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
    
    from Backend.polls_management import GetAllPolls, AssignCandidates
    from Backend.position_management import GetAllPositions
    from Backend.audits import LogAuditEntry
    from frontend_service import GetAllCandidatesService
    
    polls_list = GetAllPolls().execute()
    polls = {p["id"]: p for p in polls_list}
    
    positions_list = GetAllPositions().execute()
    positions = {p["id"]: p for p in positions_list}
    
    candidates_list = GetAllCandidatesService().execute()
    candidates = {c["id"]: c for c in candidates_list}
    
    if not polls: print(); info("No polls found."); pause(); return
    if not candidates: print(); info("No candidates found."); pause(); return
    print()
    for pid, poll in polls.items():
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
    try: pid = int(prompt("\nEnter Poll ID: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    if poll["status"] == "open": error("Cannot modify candidates of an open poll."); pause(); return
    
    active_cands = {cid: c for cid, c in candidates.items() if c["is_active"] and c.get("is_approved", True)}
    
    for i, pos in enumerate(poll["positions"]):
        subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
        current_cands = [f"{ccid}: {candidates[ccid]['full_name']}" for ccid in pos["candidate_ids"] if ccid in candidates]
        if current_cands: print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
        else: info("No candidates assigned yet.")
        
        pos_data = positions.get(pos["position_id"], {})
        min_age = pos_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
        eligible = {cid: c for cid, c in active_cands.items() if c["age"] >= min_age}
        
        if not eligible: info("No eligible candidates found."); continue
        
        subheader("Available Candidates", THEME_ADMIN)
        for cid, c in eligible.items():
            marker = f" {GREEN}[ASSIGNED]{RESET}" if cid in pos["candidate_ids"] else ""
            print(f"    {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}) - Age: {c['age']}, Edu: {c['education']}{RESET}{marker}")
            
        if prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
            try:
                new_cand_ids = [int(x.strip()) for x in prompt("Enter Candidate IDs (comma-separated): ").split(",")]
                AssignCandidates(set(eligible.keys())).execute(pid, pos["position_id"], new_cand_ids)
                success("Candidate(s) assigned.")
                LogAuditEntry().execute("CANDIDATES_ASSIGNED", current_user["username"], f"Updated candidates for poll: {poll['title']}")
            except ValueError as e: error(f"Invalid input. {str(e)}")
            except Exception as e: error(str(e))
    pause()


# ── Voter Management ──────────────────────────────────────────────────────────

def view_all_voters():
    clear_screen()
    header("ALL REGISTERED VOTERS", THEME_ADMIN)
    
    from Backend.voters_management import GetAllVoters
    voters = GetAllVoters().execute()
    
    if not voters: print(); info("No voters registered."); pause(); return
    print()
    table_header(f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}", THEME_ADMIN)
    table_divider(70, THEME_ADMIN)
    for v in voters:
        verified = status_badge("Yes", True) if v["is_verified"] else status_badge("No", False)
        active = status_badge("Yes", True) if v["is_active"] else status_badge("No", False)
        print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {v['station_id']:<6} {verified:<19} {active}")
    vc = sum(1 for v in voters if v["is_verified"])
    uc = sum(1 for v in voters if not v["is_verified"])
    print(f"\n  {DIM}Total: {len(voters)}  │  Verified: {vc}  │  Unverified: {uc}{RESET}")
    pause()


def verify_voter(current_user):
    clear_screen()
    header("VERIFY VOTER", THEME_ADMIN)
    
    from Backend.voters_management import GetAllVoters, VerifyVoter, VerifyAllVoters
    from Backend.audits import LogAuditEntry
    
    voters_list = GetAllVoters().execute()
    voters = {v["id"]: v for v in voters_list}
    
    unverified = {vid: v for vid, v in voters.items() if not v["is_verified"]}
    if not unverified: print(); info("No unverified voters."); pause(); return
    subheader("Unverified Voters", THEME_ADMIN_ACCENT)
    for vid, v in unverified.items():
        print(f"  {THEME_ADMIN}{v['id']}.{RESET} {v['full_name']} {DIM}│ NID: {v['national_id']} │ Card: {v['voter_card_number']}{RESET}")
    print()
    menu_item(1, "Verify a single voter", THEME_ADMIN)
    menu_item(2, "Verify all pending voters", THEME_ADMIN)
    choice = prompt("\nChoice: ")
    if choice == "1":
        try: vid = int(prompt("Enter Voter ID: "))
        except ValueError: error("Invalid input."); pause(); return
        if vid not in voters: error("Voter not found."); pause(); return
        if voters[vid]["is_verified"]: info("Already verified."); pause(); return
        
        try:
            VerifyVoter().execute(vid)
            LogAuditEntry().execute("VOTER_VERIFIED", current_user["username"], f"Verified voter: {voters[vid]['full_name']}")
            print(); success(f"Voter '{voters[vid]['full_name']}' verified!")
        except Exception as e:
            error(str(e))
    elif choice == "2":
        try:
            count = VerifyAllVoters().execute()
            LogAuditEntry().execute("ALL_VOTERS_VERIFIED", current_user["username"], f"Verified {count} voters")
            print(); success(f"{count} voters verified!")
        except Exception as e:
            error(str(e))
    pause()


def deactivate_voter(current_user):
    clear_screen()
    header("DEACTIVATE VOTER", THEME_ADMIN)
    
    from Backend.voters_management import GetAllVoters, DeactivateVoter
    from Backend.audits import LogAuditEntry
    voters_list = GetAllVoters().execute()
    voters = {v["id"]: v for v in voters_list}
    
    if not voters: print(); info("No voters found."); pause(); return
    print()
    try: vid = int(prompt("Enter Voter ID to deactivate: "))
    except ValueError: error("Invalid input."); pause(); return
    if vid not in voters: error("Voter not found."); pause(); return
    if not voters[vid]["is_active"]: info("Already deactivated."); pause(); return
    if prompt(f"Deactivate '{voters[vid]['full_name']}'? (yes/no): ").lower() == "yes":
        try:
            DeactivateVoter().execute(vid)
            LogAuditEntry().execute("VOTER_DEACTIVATED", current_user["username"], f"Deactivated voter: {voters[vid]['full_name']}")
            print(); success("Voter deactivated.")
        except Exception as e:
            error(str(e))
    pause()


def search_voters():
    clear_screen()
    header("SEARCH VOTERS", THEME_ADMIN)
    subheader("Search by", THEME_ADMIN_ACCENT)
    menu_item(1, "Name", THEME_ADMIN); menu_item(2, "Voter Card Number", THEME_ADMIN)
    menu_item(3, "National ID", THEME_ADMIN); menu_item(4, "Station", THEME_ADMIN)
    choice = prompt("\nChoice: ")
    
    from Backend.voters_management import SearchVoters
    searcher = SearchVoters()
    
    results = []
    try:
        if choice == "1": term = prompt("Name: "); results = searcher.execute("name", term)
        elif choice == "2": term = prompt("Card Number: "); results = searcher.execute("card", term)
        elif choice == "3": term = prompt("National ID: "); results = searcher.execute("national_id", term)
        elif choice == "4": term = prompt("Station ID: "); results = searcher.execute("station", term)
        else: error("Invalid choice."); pause(); return
    except ValueError as e:
        error(str(e)); pause(); return
        
    if not results: print(); info("No voters found.")
    else:
        print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
        for v in results:
            verified = status_badge("Verified", True) if v['is_verified'] else status_badge("Unverified", False)
            print(f"  {THEME_ADMIN}ID:{RESET} {v['id']}  {DIM}│{RESET}  {v['full_name']}  {DIM}│  Card:{RESET} {v['voter_card_number']}  {DIM}│{RESET}  {verified}")
    pause()


# ── Admin Management ──────────────────────────────────────────────────────────

def create_admin(current_user):
    clear_screen()
    header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
    if current_user["role"] != "super_admin": print(); error("Only super admins can create admin accounts."); pause(); return
    print()
    username = prompt("Username: ")
    if not username: error("Username cannot be empty."); pause(); return
    full_name = prompt("Full Name: ")
    email = prompt("Email: ")
    password = masked_input("Password: ").strip()
    if len(password) < 6: error("Password must be at least 6 characters."); pause(); return
    subheader("Available Roles", THEME_ADMIN_ACCENT)
    menu_item(1, f"super_admin {DIM}─ Full access{RESET}", THEME_ADMIN)
    menu_item(2, f"election_officer {DIM}─ Manage polls and candidates{RESET}", THEME_ADMIN)
    menu_item(3, f"station_manager {DIM}─ Manage stations and verify voters{RESET}", THEME_ADMIN)
    menu_item(4, f"auditor {DIM}─ Read-only access{RESET}", THEME_ADMIN)
    role_choice = prompt("\nSelect role (1-4): ")
    role_map = {"1": "super_admin", "2": "election_officer", "3": "station_manager", "4": "auditor"}
    if role_choice not in role_map: error("Invalid role."); pause(); return
    role = role_map[role_choice]
    
    from Backend.admin_management import CreateAdmin
    from Backend.audits import LogAuditEntry
    try:
        CreateAdmin(current_user).execute(username, password, full_name, email, role)
        LogAuditEntry().execute("CREATE_ADMIN", current_user["username"], f"Created admin: {username} (Role: {role})")
        print(); success(f"Admin '{username}' created with role: {role}")
    except ValueError as e:
        error(str(e))
    except PermissionError as e:
        error(str(e))
    pause()


def view_admins():
    clear_screen()
    header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
    from Backend.admin_management import GetAllAdmins
    admins = GetAllAdmins().execute()
    print()
    table_header(f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}", THEME_ADMIN)
    table_divider(78, THEME_ADMIN)
    for a in admins:
        active = status_badge("Yes", True) if a["is_active"] else status_badge("No", False)
        print(f"  {a['id']:<5} {a['username']:<20} {a['full_name']:<25} {a['role']:<20} {active}")
    print(f"\n  {DIM}Total Admins: {len(admins)}{RESET}")
    pause()


def deactivate_admin(current_user):
    clear_screen()
    header("DEACTIVATE ADMIN", THEME_ADMIN)
    if current_user["role"] != "super_admin": print(); error("Only super admins can deactivate admins."); pause(); return
    
    from Backend.admin_management import GetAllAdmins, DeactivateAdmin
    from Backend.audits import LogAuditEntry
    admins_list = GetAllAdmins().execute()
    admins = {a["id"]: a for a in admins_list}
    
    print()
    for aid, a in admins.items():
        active = status_badge("Active", True) if a["is_active"] else status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{a['id']}.{RESET} {a['username']} {DIM}({a['role']}){RESET} {active}")
    try: aid = int(prompt("\nEnter Admin ID to deactivate: "))
    except ValueError: error("Invalid input."); pause(); return
    if aid not in admins: error("Admin not found."); pause(); return
    if aid == current_user["id"]: error("Cannot deactivate your own account."); pause(); return
    if prompt(f"Deactivate '{admins[aid]['username']}'? (yes/no): ").lower() == "yes":
        try:
            DeactivateAdmin(current_user).execute(aid)
            LogAuditEntry().execute("DEACTIVATE_ADMIN", current_user["username"], f"Deactivated admin: {admins[aid]['username']}")
            print(); success("Admin deactivated.")
        except Exception as e:
            error(str(e))
    pause()