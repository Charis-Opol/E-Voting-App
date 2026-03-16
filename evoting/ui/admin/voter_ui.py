class VoterUI:

    def __init__(self, voter_service, console):
        self._voter_service = voter_service
        self._console = console


    def register_voter(self):

        name = self._console.input("Full Name: ")
        national_id = self._console.input("National ID: ")
        station = self._console.input("Station ID: ")

        vid = self._voter_service.register_voter(
            name,
            national_id,
            station
        )

        self._console.print(f"Voter registered: {vid}")