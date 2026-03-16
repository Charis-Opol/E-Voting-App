class StationUI:

    def __init__(self, station_service, console):
        self._station_service = station_service
        self._console = console

    def create_station(self):

        name = self._console.input("Station Name: ")
        location = self._console.input("Location: ")
        capacity = int(self._console.input("Capacity: "))

        sid = self._station_service.create_station(
            name,
            location,
            capacity
        )

        self._console.print(f"Station created: {sid}")


    def view_stations(self):

        stations = self._station_service.get_all_stations()

        for sid, s in stations.items():
            self._console.print(
                f"{sid} | {s['name']} | {s['location']} | {s['capacity']}"
            )