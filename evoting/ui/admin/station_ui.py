class StationUI:

    def __init__(self, station_service, console):
        self._station_service = station_service
        self._console = console

    def create_station(self, admin_user):

        name = self._console.input("Station Name: ")
        location = self._console.input("Location: ")
        region = self._console.input("Region: ")
        capacity = int(self._console.input("Capacity: "))
        supervisor = self._console.input("Supervisor: ")
        contact = self._console.input("Contact: ")
        opening_time = self._console.input("Opening Time (HH:MM): ")
        closing_time = self._console.input("Closing Time (HH:MM): ")

        sid = self._station_service.create_station(
            name,
            location,
            region,
            capacity,
            supervisor,
            contact,
            opening_time,
            closing_time,
            admin_user["username"]
        )

        self._console.print(f"Station created: {sid}")


    def view_stations(self):

        stations = self._station_service.get_all_stations()

        for sid, s in stations.items():
            self._console.print(
                f"{sid} | {s['name']} | {s['location']} | {s['capacity']}"
            )