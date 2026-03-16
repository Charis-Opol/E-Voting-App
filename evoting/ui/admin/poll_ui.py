class PollUI:

    def __init__(self, poll_service, console):
        self._poll_service = poll_service
        self._console = console

    def create_poll(self, admin_user):

        name = self._console.input("Poll Title: ")
        desc = self._console.input("Description: ")
        etype = self._console.input("Election Type (e.g. National, Local): ")
        start = self._console.input("Start Date (YYYY-MM-DD): ")
        end = self._console.input("End Date (YYYY-MM-DD): ")
        
        # In a real app, we'd loop to add positions/stations.
        # For now, we'll use empty lists or simple inputs to avoid TypeError.
        self._console.print_info("(Extended poll configuration skipped for brevity)")
        poll_positions = [] 
        station_ids = []

        pid = self._poll_service.create_poll(
            name, desc, etype, start, end,
            poll_positions, station_ids, admin_user["username"]
        )

        self._console.print_success(f"Poll created with ID: {pid}")


    def view_polls(self):

        polls = self._poll_service.get_all_polls()

        for pid, p in polls.items():
            self._console.print(
                f"{pid} | {p['name']} | {p['status']}"
            )