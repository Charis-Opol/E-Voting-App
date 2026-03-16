class AdminDashboard:

    def __init__(
        self,
        console,
        candidate_ui,
        station_ui,
        poll_ui,
        voter_ui,
        admin_ui,
        report_ui
    ):

        self.console = console
        self.candidate_ui = candidate_ui
        self.station_ui = station_ui
        self.poll_ui = poll_ui
        self.voter_ui = voter_ui
        self.admin_ui = admin_ui
        self.report_ui = report_ui


    def show(self):

        while True:

            self.console.print("\nADMIN DASHBOARD")

            self.console.print("1. Create Candidate")
            self.console.print("2. View Candidates")
            self.console.print("3. Create Station")
            self.console.print("4. View Stations")
            self.console.print("5. Create Poll")
            self.console.print("6. View Polls")
            self.console.print("7. Register Voter")
            self.console.print("8. View Results")
            self.console.print("9. View Admins")
            self.console.print("10. View Audit Log")
            self.console.print("0. Logout")

            choice = self.console.input("Select option: ")

            if choice == "1":
                self.candidate_ui.create_candidate()

            elif choice == "2":
                self.candidate_ui.view_candidates()

            elif choice == "3":
                self.station_ui.create_station()

            elif choice == "4":
                self.station_ui.view_stations()

            elif choice == "5":
                self.poll_ui.create_poll()

            elif choice == "6":
                self.poll_ui.view_polls()

            elif choice == "7":
                self.voter_ui.register_voter()

            elif choice == "8":
                self.report_ui.view_results()

            elif choice == "9":
                self.admin_ui.view_admins()

            elif choice == "10":
                self.admin_ui.view_audit_log()

            elif choice == "0":
                break