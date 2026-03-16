class AdminUI:

    def __init__(self, admin_service, console):
        self._admin_service = admin_service
        self._console = console


    def view_admins(self):

        admins = self._admin_service.get_all_admins()

        for a in admins:
            self._console.print(a["username"])


    def view_audit_log(self):

        logs = self._admin_service.get_audit_log()

        for log in logs:
            self._console.print(log)