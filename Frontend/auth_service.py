import random
import string
from security import hash_password


class AuthService:

    def __init__(self, storage):
        self.storage = storage

    def generate_voter_card(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


    def admin_login(self):

        username = input("Username: ")
        password = input("Password: ")

        for admin in self.storage.admins.values():

            if admin["username"] == username and admin["password"] == password:
                print("Admin login successful")
                return admin

        print("Invalid credentials")
        return None


    def voter_login(self):

        card = input("Voter Card Number: ")
        password = input("Password: ")

        hashed = hash_password(password)

        for voter in self.storage.voters.values():

            if voter["voter_card"] == card and voter["password"] == hashed:
                print("Voter login successful")
                return voter

        print("Invalid voter credentials")
        return None


    def register_voter(self):

        name = input("Full Name: ")
        national_id = input("National ID: ")
        password = input("Password: ")

        voter_card = self.generate_voter_card()

        voter_id = len(self.storage.voters) + 1

        self.storage.voters[voter_id] = {
            "id": voter_id,
            "name": name,
            "national_id": national_id,
            "voter_card": voter_card,
            "password": hash_password(password)
        }

        print("\nRegistration successful")
        print("Your Voter Card:", voter_card)