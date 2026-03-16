"""
ui/voter_dashboard.py
Responsibility: Render the voter menu and route choices to service calls.
Zero business logic — only UI flow + service calls.
"""

from ui.console import (
    clear_screen, header, status_badge, subheader, menu_item, prompt, pause,
    masked_input, print_error, print_success, print_warning, print_info,
    THEME_VOTER, THEME_VOTER_ACCENT, BRIGHT_WHITE, BOLD, DIM, RESET,
    GREEN, RED, YELLOW, GRAY, BG_GREEN, BLACK, BRIGHT_GREEN, BRIGHT_YELLOW,
    BRIGHT_CYAN, ITALIC,
)
from services.vote_service import VoteService
from services.auth_service import AuthService


class VoterDashboard:
    """Top-level voter UI. Each menu action calls exactly one service method."""

    def __init__(self, current_user: dict,
                 vote_svc:  VoteService,
                 auth_svc:  AuthService,
                 store):
        self._user  = current_user
        self._vote  = vote_svc
        self._auth  = auth_svc
        self._store = store

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        while True:
            clear_screen()
            header("VOTER DASHBOARD", THEME_VOTER)
            station_name = self._store.voting_stations.get(
                self._user["station_id"], {}
            ).get("name", "Unknown")
            print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{self._user['full_name']}{RESET}")
            print(f"  {DIM}    Card: {self._user['voter_card_number']}  │  Station: {station_name}{RESET}")
            print()
            menu_item(1, "View Open Polls",              THEME_VOTER)
            menu_item(2, "Cast Vote",                    THEME_VOTER)
            menu_item(3, "View My Voting History",       THEME_VOTER)
            menu_item(4, "View Results (Closed Polls)",  THEME_VOTER)
            menu_item(5, "View My Profile",              THEME_VOTER)
            menu_item(6, "Change Password",              THEME_VOTER)
            menu_item(7, "Logout",                       THEME_VOTER)
            print()
            choice = prompt("Enter choice: ")

            if   choice == "1": self._view_open_polls()
            elif choice == "2": self._cast_vote()
            elif choice == "3": self._view_voting_history()
            elif choice == "4": self._view_closed_poll_results()
            elif choice == "5": self._view_profile()
            elif choice == "6": self._change_password()
            elif choice == "7":
                self._auth.logout_voter(self._user)
                break
            else:
                print_error("Invalid choice.")
                pause()

    # ── Screens ──────────────────────────────────────────────────────────────

    def _view_open_polls(self):
        clear_screen()
        header("OPEN POLLS", THEME_VOTER)
        open_polls = self._vote.get_open_polls()
        if not open_polls:
            print(); print_info("No open polls at this time."); pause(); return
        for pid, poll in open_polls.items():
            already_voted = pid in self._user.get("has_voted_in", [])
            vs = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {YELLOW}[NOT YET VOTED]{RESET}"
            print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll['id']}: {poll['title']}{RESET}{vs}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Period:{RESET} {poll['start_date']} to {poll['end_date']}")
            for pos in poll["positions"]:
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
                for ccid in pos["candidate_ids"]:
                    c = self._store.candidates.get(ccid)
                    if c:
                        print(f"      {DIM}•{RESET} {c['full_name']} {DIM}({c['party']}) │ Age: {c['age']} │ Edu: {c['education']}{RESET}")
        pause()

    def _cast_vote(self):
        clear_screen()
        header("CAST YOUR VOTE", THEME_VOTER)
        available_polls = self._vote.get_available_polls_for_voter(self._user)
        if not available_polls:
            print(); print_info("No available polls to vote in."); pause(); return

        subheader("Available Polls", THEME_VOTER_ACCENT)
        for pid, poll in available_polls.items():
            print(f"  {THEME_VOTER}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['election_type']}){RESET}")

        try:
            pid = int(prompt("\nSelect Poll ID to vote: "))
        except ValueError:
            print_error("Invalid input."); pause(); return
        if pid not in available_polls:
            print_error("Invalid poll selection."); pause(); return

        poll = self._store.polls[pid]
        print()
        header(f"Voting: {poll['title']}", THEME_VOTER)
        print_info("Please select ONE candidate for each position.\n")

        vote_selections = []
        for pos in poll["positions"]:
            subheader(pos["position_title"], THEME_VOTER_ACCENT)
            if not pos["candidate_ids"]:
                print_info("No candidates for this position.")
                continue
            for idx, ccid in enumerate(pos["candidate_ids"], 1):
                c = self._store.candidates.get(ccid)
                if c:
                    print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
                    print(f"       {DIM}Age: {c['age']} │ Edu: {c['education']} │ Exp: {c['years_experience']} yrs{RESET}")
                    if c["manifesto"]:
                        print(f"       {ITALIC}{DIM}{c['manifesto'][:80]}...{RESET}")
            print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")

            try:
                vote_choice = int(prompt(f"\nYour choice for {pos['position_title']}: "))
            except ValueError:
                print_warning("Invalid input. Skipping.")
                vote_choice = 0

            if vote_choice == 0:
                vote_selections.append({
                    "position_id":    pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id":   None,
                    "abstained":      True,
                })
            elif 1 <= vote_choice <= len(pos["candidate_ids"]):
                selected_cid = pos["candidate_ids"][vote_choice - 1]
                vote_selections.append({
                    "position_id":    pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id":   selected_cid,
                    "candidate_name": self._store.candidates[selected_cid]["full_name"],
                    "abstained":      False,
                })
            else:
                print_warning("Invalid choice. Marking as abstain.")
                vote_selections.append({
                    "position_id":    pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id":   None,
                    "abstained":      True,
                })

        subheader("VOTE SUMMARY", BRIGHT_WHITE)
        for sel in vote_selections:
            if sel["abstained"]:
                print(f"  {sel['position_title']}: {GRAY}ABSTAINED{RESET}")
            else:
                print(f"  {sel['position_title']}: {BRIGHT_GREEN}{BOLD}{sel['candidate_name']}{RESET}")

        print()
        if prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
            print_info("Vote cancelled."); pause(); return

        vote_hash = self._vote.cast_votes(self._user, pid, vote_selections)
        print()
        print_success("Your vote has been recorded successfully!")
        print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{vote_hash}{RESET}")
        print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
        pause()

    def _view_voting_history(self):
        clear_screen()
        header("MY VOTING HISTORY", THEME_VOTER)
        voted_polls = self._user.get("has_voted_in", [])
        if not voted_polls:
            print(); print_info("You have not voted in any polls yet."); pause(); return

        print(f"\n  {DIM}You have voted in {len(voted_polls)} poll(s):{RESET}\n")
        for pid in voted_polls:
            poll = self._store.polls.get(pid)
            if not poll:
                continue
            sc = GREEN if poll["status"] == "open" else RED
            print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: {poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{poll['status'].upper()}{RESET}")
            for vr in self._vote.get_voter_vote_records(self._user["id"], pid):
                pos_title = next(
                    (pos["position_title"] for pos in poll.get("positions", [])
                     if pos["position_id"] == vr["position_id"]),
                    "Unknown",
                )
                if vr["abstained"]:
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {GRAY}ABSTAINED{RESET}")
                else:
                    cand_name = self._store.candidates.get(vr["candidate_id"], {}).get("full_name", "Unknown")
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {BRIGHT_GREEN}{cand_name}{RESET}")
            print()
        pause()

    def _view_closed_poll_results(self):
        clear_screen()
        header("ELECTION RESULTS", THEME_VOTER)
        closed_polls = self._vote.get_closed_polls()
        if not closed_polls:
            print(); print_info("No closed polls with results."); pause(); return

        for pid, poll in closed_polls.items():
            print(f"\n  {BOLD}{THEME_VOTER}{poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
            for pos in poll["positions"]:
                subheader(pos["position_title"], THEME_VOTER_ACCENT)
                vote_counts   = {}
                abstain_count = 0
                for v in self._store.votes:
                    if v["poll_id"] == pid and v["position_id"] == pos["position_id"]:
                        if v["abstained"]:
                            abstain_count += 1
                        else:
                            vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
                total = sum(vote_counts.values()) + abstain_count
                for rank, (cid, count) in enumerate(
                    sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1
                ):
                    cand   = self._store.candidates.get(cid, {})
                    pct    = (count / total * 100) if total > 0 else 0
                    bar    = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                    winner = f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}" if rank <= pos["max_winners"] else ""
                    print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                    print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
                if abstain_count > 0:
                    print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count/total*100) if total>0 else 0:.1f}%){RESET}")
        pause()

    def _view_profile(self):
        clear_screen()
        header("MY PROFILE", THEME_VOTER)
        v = self._user
        station_name = self._store.voting_stations.get(v["station_id"], {}).get("name", "Unknown")
        verified_badge = status_badge("Yes", True) if v["is_verified"] else status_badge("No", False)
        print()
        profile_rows = [
            ("Name",          v["full_name"]),
            ("National ID",   v["national_id"]),
            ("Voter Card",    f"{BRIGHT_YELLOW}{v['voter_card_number']}{RESET}"),
            ("Date of Birth", v["date_of_birth"]),
            ("Age",           v["age"]),
            ("Gender",        v["gender"]),
            ("Address",       v["address"]),
            ("Phone",         v["phone"]),
            ("Email",         v["email"]),
            ("Station",       station_name),
            ("Verified",      verified_badge),
            ("Registered",    v["registered_at"]),
            ("Polls Voted",   len(v.get("has_voted_in", []))),
        ]
        for label, value in profile_rows:
            print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
        pause()

    def _change_password(self):
        clear_screen()
        header("CHANGE PASSWORD", THEME_VOTER)
        print()
        old_pass     = masked_input("Current Password: ").strip()
        new_pass     = masked_input("New Password: ").strip()
        confirm_pass = masked_input("Confirm New Password: ").strip()

        ok, err = self._auth.change_voter_password(
            self._user, old_pass, new_pass, confirm_pass
        )
        if ok:
            print(); print_success("Password changed successfully!")
        else:
            print_error(err)
        pause()
