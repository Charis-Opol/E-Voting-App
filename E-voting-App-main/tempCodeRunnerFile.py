### poll crud
def create_poll():
    global poll_id_counter
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
    if not positions: error("No positions available. Create positions first."); pause(); return
    subheader("Available Positions", THEME_ADMIN_ACCENT)
    active_positions = {pid: p for pid, p in positions.items() if p["is_active"]}
    if not active_positions: error("No active positions."); pause(); return
    for pid, p in active_positions.items():
        print(f"    {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}) - {p['max_winners']} seat(s){RESET}")
    try: selected_position_ids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
    except ValueError: error("Invalid input."); pause(); return
    poll_positions = []
    for spid in selected_position_ids:
        if spid not in active_positions: warning(f"Position ID {spid} not found or inactive. Skipping."); continue
        poll_positions.append({"position_id": spid, "position_title": positions[spid]["title"], "candidate_ids": [], "max_winners": positions[spid]["max_winners"]})
    if not poll_positions: error("No valid positions selected."); pause(); return
    if not voting_stations: error("No voting stations. Create stations first."); pause(); return
    subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
    active_stations = {sid: s for sid, s in voting_stations.items() if s["is_active"]}
    for sid, s in active_stations.items():
        print(f"    {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET}")
    if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
        selected_station_ids = list(active_stations.keys())
    else:
        try: selected_station_ids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
        except ValueError: error("Invalid input."); pause(); return
    polls[poll_id_counter] = {
        "id": poll_id_counter, "title": title, "description": description,
        "election_type": election_type, "start_date": start_date, "end_date": end_date,
        "positions": poll_positions, "station_ids": selected_station_ids,
        "status": "draft", "total_votes_cast": 0,
        "created_at": str(datetime.datetime.now()), "created_by": current_user["username"]
    }
    log_action("CREATE_POLL", current_user["username"], f"Created poll: {title} (ID: {poll_id_counter})")
    print(); success(f"Poll '{title}' created! ID: {poll_id_counter}")
    warning("Status: DRAFT - Assign candidates and then open the poll.")
    poll_id_counter += 1
    save_data(); pause()


def view_all_polls():
    clear_screen()
    header("ALL POLLS / ELECTIONS", THEME_ADMIN)
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


def update_poll():
    clear_screen()
    header("UPDATE POLL", THEME_ADMIN)
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
    new_title = prompt(f"Title [{poll['title']}]: ")
    if new_title: poll["title"] = new_title
    new_desc = prompt(f"Description [{poll['description'][:50]}]: ")
    if new_desc: poll["description"] = new_desc
    new_type = prompt(f"Election Type [{poll['election_type']}]: ")
    if new_type: poll["election_type"] = new_type
    new_start = prompt(f"Start Date [{poll['start_date']}]: ")
    if new_start:
        try: datetime.datetime.strptime(new_start, "%Y-%m-%d"); poll["start_date"] = new_start
        except ValueError: warning("Invalid date, keeping old value.")
    new_end = prompt(f"End Date [{poll['end_date']}]: ")
    if new_end:
        try: datetime.datetime.strptime(new_end, "%Y-%m-%d"); poll["end_date"] = new_end
        except ValueError: warning("Invalid date, keeping old value.")
    log_action("UPDATE_POLL", current_user["username"], f"Updated poll: {poll['title']}")
    print(); success("Poll updated!")
    save_data(); pause()


def delete_poll():
    clear_screen()
    header("DELETE POLL", THEME_ADMIN)
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
        del polls[pid]
        global votes
        votes = [v for v in votes if v["poll_id"] != pid]
        log_action("DELETE_POLL", current_user["username"], f"Deleted poll: {deleted_title}")
        print(); success(f"Poll '{deleted_title}' deleted.")
        save_data()
    pause()


def open_close_poll():
    clear_screen()
    header("OPEN / CLOSE POLL", THEME_ADMIN)
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']}  {sc}{BOLD}{poll['status'].upper()}{RESET}")
    try: pid = int(prompt("\nEnter Poll ID: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    if poll["status"] == "draft":
        if not any(pos["candidate_ids"] for pos in poll["positions"]): error("Cannot open - no candidates assigned."); pause(); return
        if prompt(f"Open poll '{poll['title']}'? Voting will begin. (yes/no): ").lower() == "yes":
            poll["status"] = "open"
            log_action("OPEN_POLL", current_user["username"], f"Opened poll: {poll['title']}")
            print(); success(f"Poll '{poll['title']}' is now OPEN for voting!")
            save_data()
    elif poll["status"] == "open":
        if prompt(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): ").lower() == "yes":
            poll["status"] = "closed"
            log_action("CLOSE_POLL", current_user["username"], f"Closed poll: {poll['title']}")
            print(); success(f"Poll '{poll['title']}' is now CLOSED.")
            save_data()
    elif poll["status"] == "closed":
        info("This poll is already closed.")
        if prompt("Reopen it? (yes/no): ").lower() == "yes":
            poll["status"] = "open"
            log_action("REOPEN_POLL", current_user["username"], f"Reopened poll: {poll['title']}")
            print(); success("Poll reopened!")
            save_data()
    pause()


def assign_candidates_to_poll():
    clear_screen()
    header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
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
    for i, pos in enumerate(poll["positions"]):
        subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
        current_cands = [f"{ccid}: {candidates[ccid]['full_name']}" for ccid in pos["candidate_ids"] if ccid in candidates]
        if current_cands: print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
        else: info("No candidates assigned yet.")
        active_candidates = {cid: c for cid, c in candidates.items() if c["is_active"] and c["is_approved"]}
        pos_data = positions.get(pos["position_id"], {})
        min_age = pos_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
        eligible = {cid: c for cid, c in active_candidates.items() if c["age"] >= min_age}
        if not eligible: info("No eligible candidates found."); continue
        subheader("Available Candidates", THEME_ADMIN)
        for cid, c in eligible.items():
            marker = f" {GREEN}[ASSIGNED]{RESET}" if cid in pos["candidate_ids"] else ""
            print(f"    {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}) - Age: {c['age']}, Edu: {c['education']}{RESET}{marker}")
        if prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
            try:
                new_cand_ids = [int(x.strip()) for x in prompt("Enter Candidate IDs (comma-separated): ").split(",")]
                valid_ids = []
                for ncid in new_cand_ids:
                    if ncid in eligible: valid_ids.append(ncid)
                    else: warning(f"Candidate {ncid} not eligible. Skipping.")
                pos["candidate_ids"] = valid_ids
                success(f"{len(valid_ids)} candidate(s) assigned.")
            except ValueError: error("Invalid input. Skipping this position.")
    log_action("ASSIGN_CANDIDATES", current_user["username"], f"Updated candidates for poll: {poll['title']}")
    save_data(); pause()


### voter management
def view_all_voters():
    clear_screen()
    header("ALL REGISTERED VOTERS", THEME_ADMIN)
    if not voters: print(); info("No voters registered."); pause(); return
    print()
    table_header(f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}", THEME_ADMIN)
    table_divider(70, THEME_ADMIN)
    for vid, v in voters.items():
        verified = status_badge("Yes", True) if v["is_verified"] else status_badge("No", False)
        active = status_badge("Yes", True) if v["is_active"] else status_badge("No", False)
        print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {v['station_id']:<6} {verified:<19} {active}")
    verified_count = sum(1 for v in voters.values() if v["is_verified"])
    unverified_count = sum(1 for v in voters.values() if not v["is_verified"])
    print(f"\n  {DIM}Total: {len(voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}{RESET}")
    pause()


def verify_voter():
    clear_screen()
    header("VERIFY VOTER", THEME_ADMIN)
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
        voters[vid]["is_verified"] = True
        log_action("VERIFY_VOTER", current_user["username"], f"Verified voter: {voters[vid]['full_name']}")
        print(); success(f"Voter '{voters[vid]['full_name']}' verified!")
        save_data()
    elif choice == "2":
        count = 0
        for vid in unverified: voters[vid]["is_verified"] = True; count += 1
        log_action("VERIFY_ALL_VOTERS", current_user["username"], f"Verified {count} voters")
        print(); success(f"{count} voters verified!")
        save_data()
    pause()


def deactivate_voter():
    clear_screen()
    header("DEACTIVATE VOTER", THEME_ADMIN)
    if not voters: print(); info("No voters found."); pause(); return
    print()
    try: vid = int(prompt("Enter Voter ID to deactivate: "))
    except ValueError: error("Invalid input."); pause(); return
    if vid not in voters: error("Voter not found."); pause(); return
    if not voters[vid]["is_active"]: info("Already deactivated."); pause(); return
    if prompt(f"Deactivate '{voters[vid]['full_name']}'? (yes/no): ").lower() == "yes":
        voters[vid]["is_active"] = False
        log_action("DEACTIVATE_VOTER", current_user["username"], f"Deactivated voter: {voters[vid]['full_name']}")
        print(); success("Voter deactivated.")
        save_data()
    pause()


def search_voters():
    clear_screen()
    header("SEARCH VOTERS", THEME_ADMIN)
    subheader("Search by", THEME_ADMIN_ACCENT)
    menu_item(1, "Name", THEME_ADMIN); menu_item(2, "Voter Card Number", THEME_ADMIN)
    menu_item(3, "National ID", THEME_ADMIN); menu_item(4, "Station", THEME_ADMIN)
    choice = prompt("\nChoice: ")
    results = []
    if choice == "1": term = prompt("Name: ").lower(); results = [v for v in voters.values() if term in v["full_name"].lower()]
    elif choice == "2": term = prompt("Card Number: "); results = [v for v in voters.values() if term == v["voter_card_number"]]
    elif choice == "3": term = prompt("National ID: "); results = [v for v in voters.values() if term == v["national_id"]]
    elif choice == "4":
        try: sid = int(prompt("Station ID: ")); results = [v for v in voters.values() if v["station_id"] == sid]
        except ValueError: error("Invalid input."); pause(); return
    else: error("Invalid choice."); pause(); return
    if not results: print(); info("No voters found.")
    else:
        print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
        for v in results:
            verified = status_badge("Verified", True) if v['is_verified'] else status_badge("Unverified", False)
            print(f"  {THEME_ADMIN}ID:{RESET} {v['id']}  {DIM}│{RESET}  {v['full_name']}  {DIM}│  Card:{RESET} {v['voter_card_number']}  {DIM}│{RESET}  {verified}")
    pause()


### admin management
def create_admin():
    global admin_id_counter
    clear_screen()
    header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
    if current_user["role"] != "super_admin": print(); error("Only super admins can create admin accounts."); pause(); return
    print()
    username = prompt("Username: ")
    if not username: error("Username cannot be empty."); pause(); return
    for aid, a in admins.items():
        if a["username"] == username: error("Username already exists."); pause(); return
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
    admins[admin_id_counter] = {
        "id": admin_id_counter, "username": username, "password": hash_password(password),
        "full_name": full_name, "email": email, "role": role,
        "created_at": str(datetime.datetime.now()), "is_active": True
    }
    log_action("CREATE_ADMIN", current_user["username"], f"Created admin: {username} (Role: {role})")
    print(); success(f"Admin '{username}' created with role: {role}")
    admin_id_counter += 1
    save_data(); pause()


def view_admins():
    clear_screen()
    header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
    print()
    table_header(f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}", THEME_ADMIN)
    table_divider(78, THEME_ADMIN)
    for aid, a in admins.items():
        active = status_badge("Yes", True) if a["is_active"] else status_badge("No", False)
        print(f"  {a['id']:<5} {a['username']:<20} {a['full_name']:<25} {a['role']:<20} {active}")
    print(f"\n  {DIM}Total Admins: {len(admins)}{RESET}")
    pause()


def deactivate_admin():
    clear_screen()
    header("DEACTIVATE ADMIN", THEME_ADMIN)
    if current_user["role"] != "super_admin": print(); error("Only super admins can deactivate admins."); pause(); return
    print()
    for aid, a in admins.items():
        active = status_badge("Active", True) if a["is_active"] else status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{a['id']}.{RESET} {a['username']} {DIM}({a['role']}){RESET} {active}")
    try: aid = int(prompt("\nEnter Admin ID to deactivate: "))
    except ValueError: error("Invalid input."); pause(); return
    if aid not in admins: error("Admin not found."); pause(); return
    if aid == current_user["id"]: error("Cannot deactivate your own account."); pause(); return
    if prompt(f"Deactivate '{admins[aid]['username']}'? (yes/no): ").lower() == "yes":
        admins[aid]["is_active"] = False
        log_action("DEACTIVATE_ADMIN", current_user["username"], f"Deactivated admin: {admins[aid]['username']}")
        print(); success("Admin deactivated.")
        save_data()
    pause()