import json
import os

class DataStorage:

    def __init__(self):

        self.voters = {}
        self.candidates = {}

        self.admins = {
            1: {
                "username": "admin",
                "password": "admin123"
            }
        }

    def save(self, filename="evoting_data.json"):

        data = {
            "voters": self.voters,
            "admins": self.admins,
            "candidates": self.candidates
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, filename="evoting_data.json"):

        if not os.path.exists(filename):
            return

        with open(filename, "r") as f:
            data = json.load(f)

        self.voters = data.get("voters", {})
        self.admins = data.get("admins", {})
        self.candidates = data.get("candidates", {})