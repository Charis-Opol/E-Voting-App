"""
voter_dashboard.py

Voter-facing features extracted from the monolithic console app.
Handles: voter dashboard menu, viewing open polls, casting a vote,
viewing voting history, viewing closed poll results, viewing profile,
and changing password.

Design: each method is small and focused (Clean Code).
All data access goes through the DatabaseEngine (separation of concerns).
"""

import hashlib
import datetime

from ui import UI
from colors import (
    RESET, BOLD, DIM, ITALIC, GRAY,
    GREEN, RED, YELLOW,
    BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_BLUE, BRIGHT_WHITE, BRIGHT_CYAN,
    BG_GREEN, BLACK,
    THEME_VOTER, THEME_VOTER_ACCENT,
)


class VoterDashboard:
    """Interactive dashboard shown after a voter logs in."""

    def __init__(self, db, current_user):
        self.db  = db
        self.user = current_user
        self.ui  = UI()

    # ── Main loop ─────────────────────────────────────────────────────────

    def run(self):
        while True:
            self.ui.clear_screen()
            self._show_dashboard_header()
            choice = self.ui.prompt("Enter choice: ")

            if   choice == "1": self.view_open_polls()
            elif choice == "2": self.cast_vote()
            elif choice == "3": self.view_voting_history()
            elif choice == "4": self.view_closed_poll_results()
            elif choice == "5": self.view_profile()
            elif choice == "6": self.change_password()
            elif choice == "7":
                self.db.log_action("LOGOUT", self.user["voter_card_number"], "Voter logged out")
                break
            else:
                self.ui.error("Invalid choice.")
                self.ui.pause()

    # ── Dashboard header ──────────────────────────────────────────────────

    def _show_dashboard_header(self):
        self.ui.header("VOTER DASHBOARD", THEME_VOTER)
        stations = self.db.get_all("voting_stations")
        station = stations.get(self.user["station_id"], {})
        station_name = station.get("name", "Unknown")
        print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{self.user['full_name']}{RESET}")
        print(f"  {DIM}    Card: {self.user['voter_card_number']}  │  Station: {station_name}{RESET}")
        print()
        self.ui.menu_item(1, "View Open Polls",           THEME_VOTER)
        self.ui.menu_item(2, "Cast Vote",                  THEME_VOTER)
        self.ui.menu_item(3, "View My Voting History",     THEME_VOTER)
        self.ui.menu_item(4, "View Results (Closed Polls)",THEME_VOTER)
        self.ui.menu_item(5, "View My Profile",            THEME_VOTER)
        self.ui.menu_item(6, "Change Password",            THEME_VOTER)
        self.ui.menu_item(7, "Logout",                     THEME_VOTER)
        print()

    # ── 1. View open polls ────────────────────────────────────────────────

    def view_open_polls(self):
        self.ui.clear_screen()
        self.ui.header("OPEN POLLS", THEME_VOTER)
        polls      = self.db.get_all("polls")
        candidates = self.db.get_all("candidates")
        open_polls = {pid: p for pid, p in polls.items() if p["status"] == "open"}

        if not open_polls:
            print()
            self.ui.info("No open polls at this time.")
            self.ui.pause()
            return

        for pid, poll in open_polls.items():
            already_voted = pid in self.user.get("has_voted_in", [])
            badge = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {YELLOW}[NOT YET VOTED]{RESET}"
            print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll['id']}: {poll['title']}{RESET}{badge}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Period:{RESET} {poll['start_date']} to {poll['end_date']}")
            for pos in poll["positions"]:
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
                for cid in pos["candidate_ids"]:
                    if cid in candidates:
                        c = candidates[cid]
                        print(f"      {DIM}•{RESET} {c['full_name']} {DIM}({c['party']}) │ Age: {c['age']} │ Edu: {c['education']}{RESET}")
        self.ui.pause()

    # ── 2. Cast vote ──────────────────────────────────────────────────────

    def cast_vote(self):
        self.ui.clear_screen()
        self.ui.header("CAST YOUR VOTE", THEME_VOTER)
        polls      = self.db.get_all("polls")
        candidates = self.db.get_all("candidates")

        open_polls = {pid: p for pid, p in polls.items() if p["status"] == "open"}
        if not open_polls:
            print()
            self.ui.info("No open polls at this time.")
            self.ui.pause()
            return

        # Filter polls the voter hasn't voted in yet and is assigned to
        available = {}
        for pid, poll in open_polls.items():
            if pid not in self.user.get("has_voted_in", []) and self.user["station_id"] in poll["station_ids"]:
                available[pid] = poll

        if not available:
            print()
            self.ui.info("No available polls to vote in.")
            self.ui.pause()
            return

        self.ui.subheader("Available Polls", THEME_VOTER_ACCENT)
        for pid, poll in available.items():
            print(f"  {THEME_VOTER}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['election_type']}){RESET}")

        try:
            pid = int(self.ui.prompt("Select Poll ID to vote: "))
        except ValueError:
            self.ui.error("Invalid input.")
            self.ui.pause()
            return
        if pid not in available:
            self.ui.error("Invalid poll selection.")
            self.ui.pause()
            return

        poll = polls[pid]
        print()
        self.ui.header(f"Voting: {poll['title']}", THEME_VOTER)
        self.ui.info("Please select ONE candidate for each position.\n")

        my_votes = []
        for pos in poll["positions"]:
            self.ui.subheader(pos["position_title"], THEME_VOTER_ACCENT)
            if not pos["candidate_ids"]:
                self.ui.info("No candidates for this position.")
                continue

            for idx, cid in enumerate(pos["candidate_ids"], 1):
                if cid in candidates:
                    c = candidates[cid]
                    print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
                    print(f"       {DIM}Age: {c['age']} │ Edu: {c['education']} │ Exp: {c['years_experience']} yrs{RESET}")
                    if c.get("manifesto"):
                        print(f"       {ITALIC}{DIM}{c['manifesto'][:80]}...{RESET}")

            print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")

            try:
                vote_choice = int(self.ui.prompt(f"Your choice for {pos['position_title']}: "))
            except ValueError:
                self.ui.warning("Invalid input. Marking as abstain.")
                vote_choice = 0

            if vote_choice == 0:
                my_votes.append(self._abstain_vote(pos))
            elif 1 <= vote_choice <= len(pos["candidate_ids"]):
                selected_cid = pos["candidate_ids"][vote_choice - 1]
                my_votes.append({
                    "position_id":    pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id":   selected_cid,
                    "candidate_name": candidates[selected_cid]["full_name"],
                    "abstained":      False,
                })
            else:
                self.ui.warning("Invalid choice. Marking as abstain.")
                my_votes.append(self._abstain_vote(pos))

        # Show summary
        self.ui.subheader("VOTE SUMMARY", BRIGHT_WHITE)
        for mv in my_votes:
            if mv["abstained"]:
                print(f"  {mv['position_title']}: {GRAY}ABSTAINED{RESET}")
            else:
                print(f"  {mv['position_title']}: {BRIGHT_GREEN}{BOLD}{mv['candidate_name']}{RESET}")
        print()

        if self.ui.prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
            self.ui.info("Vote cancelled.")
            self.ui.pause()
            return

        # Record the votes
        timestamp  = str(datetime.datetime.now())
        vote_hash  = hashlib.sha256(f"{self.user['id']}{pid}{timestamp}".encode()).hexdigest()[:16]

        for mv in my_votes:
            vote_record = {
                "vote_id":     vote_hash + str(mv["position_id"]),
                "poll_id":     pid,
                "position_id": mv["position_id"],
                "candidate_id": mv["candidate_id"],
                "voter_id":    self.user["id"],
                "station_id":  self.user["station_id"],
                "timestamp":   timestamp,
                "abstained":   mv["abstained"],
            }
            self.db.append_to_list("votes", vote_record)

        # Mark voter as having voted
        self.user["has_voted_in"].append(pid)
        voters = self.db.get_all("voters")
        for vid, v in voters.items():
            if v["id"] == self.user["id"]:
                self.db.update("voters", vid, {"has_voted_in": v.get("has_voted_in", []) + [pid]})
                break

        # Increment poll total votes
        self.db.update("polls", pid, {"total_votes_cast": poll["total_votes_cast"] + 1})

        self.db.log_action("CAST_VOTE", self.user["voter_card_number"],
                           f"Voted in poll: {poll['title']} (Hash: {vote_hash})")
        print()
        self.ui.success("Your vote has been recorded successfully!")
        print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{vote_hash}{RESET}")
        print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
        self.ui.pause()

    # ── 3. Voting history ─────────────────────────────────────────────────

    def view_voting_history(self):
        self.ui.clear_screen()
        self.ui.header("MY VOTING HISTORY", THEME_VOTER)
        voted_polls = self.user.get("has_voted_in", [])
        if not voted_polls:
            print()
            self.ui.info("You have not voted in any polls yet.")
            self.ui.pause()
            return

        polls      = self.db.get_all("polls")
        votes      = self.db.get_list("votes")
        candidates = self.db.get_all("candidates")

        print(f"\n  {DIM}You have voted in {len(voted_polls)} poll(s):{RESET}\n")
        for pid in voted_polls:
            if pid in polls:
                poll = polls[pid]
                sc = GREEN if poll["status"] == "open" else RED
                print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: {poll['title']}{RESET}")
                print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{poll['status'].upper()}{RESET}")
                my_votes = [v for v in votes if v["poll_id"] == pid and v["voter_id"] == self.user["id"]]
                for vr in my_votes:
                    pos_title = next(
                        (p["position_title"] for p in poll.get("positions", []) if p["position_id"] == vr["position_id"]),
                        "Unknown"
                    )
                    if vr["abstained"]:
                        print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {GRAY}ABSTAINED{RESET}")
                    else:
                        cand_name = candidates.get(vr["candidate_id"], {}).get("full_name", "Unknown")
                        print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {BRIGHT_GREEN}{cand_name}{RESET}")
                print()
        self.ui.pause()

    # ── 4. Closed poll results ────────────────────────────────────────────

    def view_closed_poll_results(self):
        self.ui.clear_screen()
        self.ui.header("ELECTION RESULTS", THEME_VOTER)
        polls      = self.db.get_all("polls")
        votes      = self.db.get_list("votes")
        candidates = self.db.get_all("candidates")

        closed = {pid: p for pid, p in polls.items() if p["status"] == "closed"}
        if not closed:
            print()
            self.ui.info("No closed polls with results.")
            self.ui.pause()
            return

        for pid, poll in closed.items():
            print(f"\n  {BOLD}{THEME_VOTER}{poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
            for pos in poll["positions"]:
                self.ui.subheader(pos["position_title"], THEME_VOTER_ACCENT)
                vote_counts, abstain_count = self._tally_position(votes, pid, pos["position_id"])
                total = sum(vote_counts.values()) + abstain_count
                for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                    cand = candidates.get(cid, {})
                    pct  = (count / total * 100) if total > 0 else 0
                    bar  = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                    winner = f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}" if rank <= pos["max_winners"] else ""
                    print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                    print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
                if abstain_count > 0:
                    print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total * 100) if total > 0 else 0:.1f}%){RESET}")
        self.ui.pause()

    # ── 5. View profile ───────────────────────────────────────────────────

    def view_profile(self):
        self.ui.clear_screen()
        self.ui.header("MY PROFILE", THEME_VOTER)
        v = self.user
        stations = self.db.get_all("voting_stations")
        station_name = stations.get(v["station_id"], {}).get("name", "Unknown")
        print()
        fields = [
            ("Name",        v["full_name"]),
            ("National ID", v["national_id"]),
            ("Voter Card",  f"{BRIGHT_YELLOW}{v['voter_card_number']}{RESET}"),
            ("Date of Birth", v["date_of_birth"]),
            ("Age",         v["age"]),
            ("Gender",      v["gender"]),
            ("Address",     v["address"]),
            ("Phone",       v["phone"]),
            ("Email",       v["email"]),
            ("Station",     station_name),
            ("Verified",    self.ui.status_badge("Yes", True) if v["is_verified"] else self.ui.status_badge("No", False)),
            ("Registered",  v["registered_at"]),
            ("Polls Voted", len(v.get("has_voted_in", []))),
        ]
        for label, value in fields:
            print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
        self.ui.pause()

    # ── 6. Change password ────────────────────────────────────────────────

    def change_password(self):
        self.ui.clear_screen()
        self.ui.header("CHANGE PASSWORD", THEME_VOTER)
        print()
        from security import hash_password

        old_pass = self.ui.masked_input("Current Password: ").strip()
        if hash_password(old_pass) != self.user["password"]:
            self.ui.error("Incorrect current password.")
            self.ui.pause()
            return

        new_pass = self.ui.masked_input("New Password: ").strip()
        if len(new_pass) < 6:
            self.ui.error("Password must be at least 6 characters.")
            self.ui.pause()
            return

        confirm_pass = self.ui.masked_input("Confirm New Password: ").strip()
        if new_pass != confirm_pass:
            self.ui.error("Passwords do not match.")
            self.ui.pause()
            return

        hashed_new = hash_password(new_pass)
        self.user["password"] = hashed_new
        voters = self.db.get_all("voters")
        for vid, v in voters.items():
            if v["id"] == self.user["id"]:
                self.db.update("voters", vid, {"password": hashed_new})
                break

        self.db.log_action("CHANGE_PASSWORD", self.user["voter_card_number"], "Password changed")
        print()
        self.ui.success("Password changed successfully!")
        self.ui.pause()

    # ── Private helpers ───────────────────────────────────────────────────

    @staticmethod
    def _abstain_vote(position):
        return {
            "position_id":    position["position_id"],
            "position_title": position["position_title"],
            "candidate_id":   None,
            "abstained":      True,
        }

    @staticmethod
    def _tally_position(votes, poll_id, position_id):
        """Returns (vote_counts_dict, abstain_count) for a position."""
        vote_counts = {}
        abstain_count = 0
        for v in votes:
            if v["poll_id"] == poll_id and v["position_id"] == position_id:
                if v["abstained"]:
                    abstain_count += 1
                else:
                    vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
        return vote_counts, abstain_count
