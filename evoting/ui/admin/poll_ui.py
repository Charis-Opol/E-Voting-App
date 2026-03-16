class PollUI:

    def __init__(self, poll_service, console):
        self._poll_service = poll_service
        self._console = console

    def create_poll(self):

        name = self._console.input("Poll Name: ")
        start = self._console.input("Start Date: ")
        end = self._console.input("End Date: ")

        pid = self._poll_service.create_poll(name, start, end)

        self._console.print(f"Poll created with ID: {pid}")


    def view_polls(self):

        polls = self._poll_service.get_all_polls()

        for pid, p in polls.items():
            self._console.print(
                f"{pid} | {p['name']} | {p['status']}"
            )