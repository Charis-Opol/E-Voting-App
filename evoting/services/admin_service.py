"""
services/admin_service.py
Responsibility: Business logic for creating, viewing, and deactivating
admin accounts.
"""

import datetime
from data.store import DataStore


ADMIN_ROLES = {
    "1": "super_admin",
    "2": "election_officer",
    "3": "station_manager",
    "4": "auditor",
}


class AdminService:

    def __init__(self, store: DataStore, audit_log_fn, hash_password_fn):
        self._store           = store
        self._log_action      = audit_log_fn
        self._hash_password   = hash_password_fn

    def create_admin(self, username, full_name, email, password,
                     role, created_by) -> tuple:
        """Returns (True, admin_id) or (False, error_message)."""
        if not username:
            return False, "Username cannot be empty."
        if any(a["username"] == username for a in self._store.admins.values()):
            return False, "Username already exists."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        if role not in ADMIN_ROLES.values():
            return False, "Invalid role."
        aid = self._store.admin_id_counter
        self._store.admins[aid] = {
            "id":         aid,
            "username":   username,
            "password":   self._hash_password(password),
            "full_name":  full_name,
            "email":      email,
            "role":       role,
            "created_at": str(datetime.datetime.now()),
            "is_active":  True,
        }
        self._log_action("CREATE_ADMIN", created_by, f"Created admin: {username} (Role: {role})")
        self._store.admin_id_counter += 1
        self._store.save()
        return True, aid

    def get_all_admins(self) -> dict:
        return self._store.admins

    def get_audit_log(self):
        return self._store.audit_log


    def deactivate_admin(self, aid: int, requesting_admin_id: int, deactivated_by: str) -> tuple:
        """Returns (True, username) or (False, error_message)."""
        if aid not in self._store.admins:
            return False, "Admin not found."
        if aid == requesting_admin_id:
            return False, "Cannot deactivate your own account."
        self._store.admins[aid]["is_active"] = False
        username = self._store.admins[aid]["username"]
        self._log_action("DEACTIVATE_ADMIN", deactivated_by, f"Deactivated admin: {username}")
        self._store.save()
        return True, username
