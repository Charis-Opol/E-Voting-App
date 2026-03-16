class ReportUI:

    def __init__(self, poll_service, console):
        self._poll_service = poll_service
        self._console = console


    def view_results(self):

        poll_id = self._console.input("Poll ID: ")

        results = self._poll_service.get_poll_results(poll_id)

        for candidate, votes in results.items():
            self._console.print(f"{candidate} : {votes}")