from ui import UI
from admin_dashboard import AdminDashboard
from auth_service import AuthService
from Backend.data_storage import DataStorage


class EVotingSystem:

    def __init__(self):

        self.storage = DataStorage()
        self.auth = AuthService(self.storage)
        self.ui = UI()

    def run(self):

        self.storage.load()

        while True:

            self.ui.show_login_menu()

            choice = self.ui.get_input("Enter choice: ")

            if choice == "1":

                admin = self.auth.admin_login()

                if admin:
                    dashboard = AdminDashboard(self.storage)
                    dashboard.run()

            elif choice == "2":
                self.auth.voter_login()

            elif choice == "3":
                self.auth.register_voter()

            elif choice == "4":
                self.storage.save()
                print("Goodbye")
                break

            else:
                self.ui.error("Invalid choice")


if __name__ == "__main__":

    system = EVotingSystem()
    system.run()