class AdminDashboard:

    def __init__(self, storage):
        self.storage = storage

    def run(self):

        while True:

            print("\nADMIN DASHBOARD")
            print("1. View Voters")
            print("2. View Candidates")
            print("3. Create Candidate")
            print("4. Logout")

            choice = input("Choice: ")

            if choice == "1":
                self.view_voters()

            elif choice == "2":
                self.view_candidates()

            elif choice == "3":
                self.create_candidate()

            elif choice == "4":
                break

            else:
                print("Invalid option")

    def view_voters(self):

        print("\nRegistered Voters")

        for voter in self.storage.voters.values():
            print(voter)


    def view_candidates(self):

        print("\nCandidates")

        for candidate in self.storage.candidates.values():
            print(candidate)


    def create_candidate(self):

        name = input("Candidate Name: ")

        candidate_id = len(self.storage.candidates) + 1

        self.storage.candidates[candidate_id] = {
            "id": candidate_id,
            "name": name
        }

        print("Candidate created")