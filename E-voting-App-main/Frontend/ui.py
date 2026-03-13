from colors import *

class UI:

    def header(self, title):

        print("\n" + "=" * 50)
        print(title.center(50))
        print("=" * 50)

    def show_login_menu(self):

        self.header("E-VOTING SYSTEM")

        print("1. Login as Admin")
        print("2. Login as Voter")
        print("3. Register as Voter")
        print("4. Exit")

    def get_input(self, message):
        return input(message).strip()

    def success(self, msg):
        print(GREEN + msg + RESET)

    def error(self, msg):
        print(RED + msg + RESET)

    def warning(self, msg):
        print(YELLOW + msg + RESET)