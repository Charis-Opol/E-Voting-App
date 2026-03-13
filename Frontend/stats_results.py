"""
stats_results.py

Admin-facing statistics and results module.
Extracted from the monolithic console app for separation of concerns.

Features:
    - View poll results (with turnout and bar charts)
    - View detailed system statistics (demographics, station load, parties)
    - Station-wise results breakdown
    - View and filter audit log
"""

from ui import UI
from colors import (
    RESET, BOLD, DIM, ITALIC, GRAY,
    GREEN, RED, YELLOW, CYAN,
    BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_WHITE, BRIGHT_CYAN,
    BG_GREEN, BLACK,
    THEME_ADMIN, THEME_ADMIN_ACCENT,
)


class StatsAndResults:
    """Admin-facing statistics and election results."""

    def __init__(self, db, current_user):
        self.db   = db
        self.user = current_user
        self.ui   = UI()

    # ── Menu ──────────────────────────────────────────────────────────────

    def run(self):
        while True:
            self.ui.clear_screen()
            self.ui.header("STATS & RESULTS", THEME_ADMIN)
            print()
            self.ui.menu_item(1, "View Poll Results",       THEME_ADMIN)
            self.ui.menu_item(2, "View Detailed Statistics", THEME_ADMIN)
            self.ui.menu_item(3, "Station-Wise Results",    THEME_ADMIN)
            self.ui.menu_item(4, "View Audit Log",          THEME_ADMIN)
            self.ui.menu_item(5, "Back",                    THEME_ADMIN)
            print()
            choice = self.ui.prompt("Enter choice: ")

            if   choice == "1": self.view_poll_results()
            elif choice == "2": self.view_detailed_statistics()
            elif choice == "3": self.station_wise_results()
            elif choice == "4": self.view_audit_log()
            elif choice == "5": break
            else:
                self.ui.error("Invalid choice.")
                self.ui.pause()

    # ── 1. Poll results ──────────────────────────────────────────────────

    def view_poll_results(self):
        self.ui.clear_screen()
        self.ui.header("POLL RESULTS", THEME_ADMIN)
        polls      = self.db.get_all("polls")
        voters     = self.db.get_all("voters")
        votes      = self.db.get_list("votes")
        candidates = self.db.get_all("candidates")

        if not polls:
            print(); self.ui.info("No polls found."); self.ui.pause(); return

        print()
        for pid, poll in polls.items():
            sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")

        try:
            pid = int(self.ui.prompt("Enter Poll ID: "))
        except ValueError:
            self.ui.error("Invalid input."); self.ui.pause(); return
        if pid not in polls:
            self.ui.error("Poll not found."); self.ui.pause(); return

        poll = polls[pid]
        print()
        self.ui.header(f"RESULTS: {poll['title']}", THEME_ADMIN)

        sc = GREEN if poll["status"] == "open" else RED
        print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}  {DIM}│  Votes:{RESET} {BOLD}{poll['total_votes_cast']}{RESET}")

        total_eligible = sum(
            1 for v in voters.values()
            if v["is_verified"] and v["is_active"] and v["station_id"] in poll["station_ids"]
        )
        turnout = (poll["total_votes_cast"] / total_eligible * 100) if total_eligible > 0 else 0
        tc = GREEN if turnout > 50 else (YELLOW if turnout > 25 else RED)
        print(f"  {DIM}Eligible:{RESET} {total_eligible}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")

        for pos in poll["positions"]:
            self.ui.subheader(f"{pos['position_title']} (Seats: {pos['max_winners']})", THEME_ADMIN_ACCENT)
            vote_counts, abstain_count, total_pos = self._tally(votes, pid, pos["position_id"])
            for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                cand = candidates.get(cid, {})
                pct  = (count / total_pos * 100) if total_pos > 0 else 0
                bl   = int(pct / 2)
                bar  = f"{THEME_ADMIN}{'█' * bl}{GRAY}{'░' * (50 - bl)}{RESET}"
                winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= pos["max_winners"] else ""
                print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
            if abstain_count > 0:
                print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total_pos * 100) if total_pos > 0 else 0:.1f}%){RESET}")
            if not vote_counts:
                self.ui.info("    No votes recorded for this position.")
        self.ui.pause()

    # ── 2. Detailed statistics ────────────────────────────────────────────

    def view_detailed_statistics(self):
        self.ui.clear_screen()
        self.ui.header("DETAILED STATISTICS", THEME_ADMIN)

        candidates = self.db.get_all("candidates")
        voters     = self.db.get_all("voters")
        stations   = self.db.get_all("voting_stations")
        polls      = self.db.get_all("polls")
        votes      = self.db.get_list("votes")

        # System overview
        self.ui.subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
        tc = len(candidates); ac = sum(1 for c in candidates.values() if c["is_active"])
        tv = len(voters);     vv = sum(1 for v in voters.values() if v["is_verified"])
        av = sum(1 for v in voters.values() if v["is_active"])
        ts = len(stations);  ast = sum(1 for s in stations.values() if s["is_active"])
        tp = len(polls)
        op = sum(1 for p in polls.values() if p["status"] == "open")
        cp = sum(1 for p in polls.values() if p["status"] == "closed")
        dp = sum(1 for p in polls.values() if p["status"] == "draft")

        print(f"  {THEME_ADMIN}Candidates:{RESET}  {tc} {DIM}(Active: {ac}){RESET}")
        print(f"  {THEME_ADMIN}Voters:{RESET}      {tv} {DIM}(Verified: {vv}, Active: {av}){RESET}")
        print(f"  {THEME_ADMIN}Stations:{RESET}    {ts} {DIM}(Active: {ast}){RESET}")
        print(f"  {THEME_ADMIN}Polls:{RESET}       {tp} {DIM}({GREEN}Open: {op}{RESET}{DIM}, {RED}Closed: {cp}{RESET}{DIM}, {YELLOW}Draft: {dp}{RESET}{DIM}){RESET}")
        print(f"  {THEME_ADMIN}Total Votes:{RESET} {len(votes)}")

        # Voter demographics
        self.ui.subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
        gender_counts = {}
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
        for v in voters.values():
            gender_counts[v.get("gender", "?")] = gender_counts.get(v.get("gender", "?"), 0) + 1
            age = v.get("age", 0)
            if   age <= 25: age_groups["18-25"] += 1
            elif age <= 35: age_groups["26-35"] += 1
            elif age <= 45: age_groups["36-45"] += 1
            elif age <= 55: age_groups["46-55"] += 1
            elif age <= 65: age_groups["56-65"] += 1
            else:           age_groups["65+"]   += 1
        for g, count in gender_counts.items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {g}: {count} ({pct:.1f}%)")
        print(f"  {BOLD}Age Distribution:{RESET}")
        for group, count in age_groups.items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) {THEME_ADMIN}{'█' * int(pct / 2)}{RESET}")

        # Station load
        self.ui.subheader("STATION LOAD", THEME_ADMIN_ACCENT)
        for sid, s in stations.items():
            vc = sum(1 for v in voters.values() if v["station_id"] == sid)
            lp = (vc / s["capacity"] * 100) if s["capacity"] > 0 else 0
            lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
            st = f"{RED}{BOLD}OVERLOADED{RESET}" if lp > 100 else f"{GREEN}OK{RESET}"
            print(f"    {s['name']}: {vc}/{s['capacity']} {lc}({lp:.0f}%){RESET} {st}")

        # Party distribution
        self.ui.subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
        party_counts = {}
        for c in candidates.values():
            if c["is_active"]:
                party_counts[c["party"]] = party_counts.get(c["party"], 0) + 1
        for party, count in sorted(party_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")

        # Education levels
        self.ui.subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
        edu_counts = {}
        for c in candidates.values():
            if c["is_active"]:
                edu_counts[c["education"]] = edu_counts.get(c["education"], 0) + 1
        for edu, count in edu_counts.items():
            print(f"    {edu}: {BOLD}{count}{RESET}")
        self.ui.pause()

    # ── 3. Station-wise results ───────────────────────────────────────────

    def station_wise_results(self):
        self.ui.clear_screen()
        self.ui.header("STATION-WISE RESULTS", THEME_ADMIN)
        polls      = self.db.get_all("polls")
        voters     = self.db.get_all("voters")
        votes      = self.db.get_list("votes")
        candidates = self.db.get_all("candidates")
        stations   = self.db.get_all("voting_stations")

        if not polls:
            print(); self.ui.info("No polls found."); self.ui.pause(); return

        print()
        for pid, poll in polls.items():
            sc = GREEN if poll["status"] == "open" else (YELLOW if poll["status"] == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")

        try:
            pid = int(self.ui.prompt("Enter Poll ID: "))
        except ValueError:
            self.ui.error("Invalid input."); self.ui.pause(); return
        if pid not in polls:
            self.ui.error("Poll not found."); self.ui.pause(); return

        poll = polls[pid]
        print()
        self.ui.header(f"STATION RESULTS: {poll['title']}", THEME_ADMIN)

        for sid in poll["station_ids"]:
            if sid not in stations:
                continue
            station = stations[sid]
            self.ui.subheader(f"{station['name']}  ({station['location']})", BRIGHT_WHITE)
            station_votes = [v for v in votes if v["poll_id"] == pid and v["station_id"] == sid]
            svc = len(set(v["voter_id"] for v in station_votes))
            ras = sum(1 for v in voters.values() if v["station_id"] == sid and v["is_verified"] and v["is_active"])
            st  = (svc / ras * 100) if ras > 0 else 0
            tc  = GREEN if st > 50 else (YELLOW if st > 25 else RED)
            print(f"  {DIM}Registered:{RESET} {ras}  {DIM}│  Voted:{RESET} {svc}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{st:.1f}%{RESET}")

            for pos in poll["positions"]:
                print(f"    {THEME_ADMIN_ACCENT}▸ {pos['position_title']}:{RESET}")
                pv = [v for v in station_votes if v["position_id"] == pos["position_id"]]
                vc = {}
                ac = 0
                for v in pv:
                    if v["abstained"]:
                        ac += 1
                    else:
                        vc[v["candidate_id"]] = vc.get(v["candidate_id"], 0) + 1
                total = sum(vc.values()) + ac
                for cid, count in sorted(vc.items(), key=lambda x: x[1], reverse=True):
                    cand = candidates.get(cid, {})
                    pct  = (count / total * 100) if total > 0 else 0
                    print(f"      {cand.get('full_name', '?')} {DIM}({cand.get('party', '?')}){RESET}: {BOLD}{count}{RESET} ({pct:.1f}%)")
                if ac > 0:
                    print(f"      {GRAY}Abstained: {ac} ({(ac / total * 100) if total > 0 else 0:.1f}%){RESET}")
        self.ui.pause()

    # ── 4. Audit log ──────────────────────────────────────────────────────

    def view_audit_log(self):
        self.ui.clear_screen()
        self.ui.header("AUDIT LOG", THEME_ADMIN)
        audit_log = self.db.get_list("audit_log")

        if not audit_log:
            print(); self.ui.info("No audit records."); self.ui.pause(); return

        print(f"\n  {DIM}Total Records: {len(audit_log)}{RESET}")
        self.ui.subheader("Filter", THEME_ADMIN_ACCENT)
        self.ui.menu_item(1, "Last 20 entries",       THEME_ADMIN)
        self.ui.menu_item(2, "All entries",            THEME_ADMIN)
        self.ui.menu_item(3, "Filter by action type",  THEME_ADMIN)
        self.ui.menu_item(4, "Filter by user",         THEME_ADMIN)

        choice = self.ui.prompt("Choice: ")
        entries = audit_log

        if choice == "1":
            entries = audit_log[-20:]
        elif choice == "3":
            action_types = list(set(e["action"] for e in audit_log))
            for i, at in enumerate(action_types, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
            try:
                at_choice = int(self.ui.prompt("Select action type: "))
                entries = [e for e in audit_log if e["action"] == action_types[at_choice - 1]]
            except (ValueError, IndexError):
                self.ui.error("Invalid choice."); self.ui.pause(); return
        elif choice == "4":
            uf = self.ui.prompt("Enter username/card number: ")
            entries = [e for e in audit_log if uf.lower() in e["user"].lower()]

        print()
        self.ui.table_header(f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}", THEME_ADMIN)
        self.ui.table_divider(100, THEME_ADMIN)
        for entry in entries:
            ac = GREEN if "CREATE" in entry["action"] or entry["action"] == "LOGIN" else (
                RED if "DELETE" in entry["action"] or "DEACTIVATE" in entry["action"] else (
                    YELLOW if "UPDATE" in entry["action"] else RESET
                )
            )
            print(f"  {DIM}{entry['timestamp'][:19]}{RESET}  {ac}{entry['action']:<25}{RESET} {entry['user']:<20} {DIM}{entry['details'][:50]}{RESET}")
        self.ui.pause()

    # ── Private helpers ───────────────────────────────────────────────────

    @staticmethod
    def _tally(votes, poll_id, position_id):
        """Returns (vote_counts, abstain_count, total_votes) for a position."""
        vote_counts  = {}
        abstain_count = 0
        total = 0
        for v in votes:
            if v["poll_id"] == poll_id and v["position_id"] == position_id:
                total += 1
                if v["abstained"]:
                    abstain_count += 1
                else:
                    vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
        return vote_counts, abstain_count, total
