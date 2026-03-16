class CandidateUI:

    def __init__(self, candidate_service, console):
        self._candidate_service = candidate_service
        self._console = console

    def create_candidate(self, admin_user):

        self._console.print("Create Candidate")

        full_name = self._console.input("Full Name: ")
        national_id = self._console.input("National ID: ")
        dob = self._console.input("Date of Birth (YYYY-MM-DD): ")
        gender = self._console.input("Gender: ")
        education = self._console.input("Education Level: ")
        party = self._console.input("Political Party: ")
        manifesto = self._console.input("Manifesto: ")
        address = self._console.input("Address: ")
        phone = self._console.input("Phone: ")
        email = self._console.input("Email: ")
        try:
            years_experience = int(self._console.input("Years Experience: "))
        except ValueError:
            self._console.print_error("Invalid input for Years Experience. Must be an integer.")
            return

        # Validate and get age
        age, error = self._candidate_service.validate_candidate(
            full_name, national_id, dob, "no" # assuming no criminal record for now or could ask
        )
        if error:
            self._console.print_error(error)
            return

        cid = self._candidate_service.create_candidate(
            full_name,
            national_id,
            dob,
            age,
            gender,
            education,
            party,
            manifesto,
            address,
            phone,
            email,
            years_experience,
            admin_user["username"],
        )

        self._console.print(f"Candidate created with ID: {cid}")


    def view_candidates(self):

        candidates = self._candidate_service.get_all_candidates()

        for cid, c in candidates.items():
            self._console.print(f"{cid} | {c['full_name']} | {c['party']}")