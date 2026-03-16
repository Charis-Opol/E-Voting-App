class VoterUI:

    def __init__(self, voter_service, auth_service, console):
        self._voter_service = voter_service
        self._auth_service = auth_service
        self._console = console


    def register_voter(self, admin_user):

        self._console.print("Register New Voter")

        name = self._console.input("Full Name: ")
        national_id = self._console.input("National ID: ")
        dob = self._console.input("Date of Birth (YYYY-MM-DD): ")
        gender = self._console.input("Gender (M/F/OTHER): ")
        address = self._console.input("Address: ")
        phone = self._console.input("Phone: ")
        email = self._console.input("Email: ")
        password = self._console.input("Password: ")
        confirm_password = self._console.input("Confirm Password: ")
        try:
            station_id = int(self._console.input("Station ID: "))
        except ValueError:
             self._console.print_error("Invalid Station ID.")
             return

        # Basic age calculation for register_voter
        from datetime import datetime
        try:
            dob_dt = datetime.strptime(dob, "%Y-%m-%d")
            age = (datetime.now() - dob_dt).days // 365
        except ValueError:
            self._console.print_error("Invalid date format.")
            return

        is_valid, error = self._auth_service.validate_voter_registration(
            name, national_id, dob, gender, password, confirm_password, station_id
        )

        if not is_valid:
            self._console.print_error(error)
            return

        card_number = self._auth_service.register_voter(
            name, national_id, dob, age, gender, address, phone, email, password, station_id
        )

        self._console.print_success(f"Voter registered! Card Number: {card_number}")