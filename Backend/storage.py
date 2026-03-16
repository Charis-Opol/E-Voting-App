"""
storage.py

One class. Reads and writes JSON files.
Every module uses this — nothing else touches the file system.
"""

import json
import os
import sys

from .api_engine import DatabaseEngine

DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database.json")

# Global singleton engine dictionary
_engines = {}

def _get_db(engine_path: str) -> DatabaseEngine:
    global _engines
    if engine_path not in _engines:
        engine = DatabaseEngine(engine_path)
        engine.load()
        _engines[engine_path] = engine
    return _engines[engine_path]


class JsonStore:
    """Acts as an adapter over the Frontend's DatabaseEngine."""

    def __init__(self, file_path: str) -> None:
        basename = os.path.basename(file_path)
        self.table_name = basename.replace(".json", "")
        
        # Mapping test files / backend files to api_engine tables
        if self.table_name == "misc":
            self.table_name = "polls"
        elif self.table_name == "audits":
            self.table_name = "audit_log"
        
        directory = os.path.dirname(file_path)
        if "test_data" in directory:
            db_path = os.path.join(directory, "database.json")
            # Always force fresh load for test data in case the directory was cleared
            engine = DatabaseEngine(db_path)
            engine.load()
            global _engines
            _engines[db_path] = engine
            self.db = engine
        else:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database.json")
            self.db = _get_db(db_path)

    # ── public adapter ────────────────────────────────────────────────────────

    def all(self) -> list[dict]:
        """Return every record in the table as a list."""
        data = self.db._data[self.table_name]
        if isinstance(data, list):
            return list(data)
        return list(data.values())

    def find(self, **field_filters) -> list[dict]:
        """Return all records where every given field matches."""
        data = self.db._data[self.table_name]
        if isinstance(data, list):
            return self.db.filter_list(self.table_name, **field_filters)
        return self.db.find(self.table_name, **field_filters)

    def find_one(self, **field_filters) -> dict | None:
        """Return the first matching record, or None if none found."""
        matching_records = self.find(**field_filters)
        return matching_records[0] if matching_records else None

    def insert(self, new_record: dict) -> dict:
        """Assign a new id to the record, save it, and return it."""
        data = self.db._data[self.table_name]
        if isinstance(data, list):
            record_id = max((r.get("id", 0) for r in data), default=0) + 1
            new_record["id"] = record_id
            self.db.append_to_list(self.table_name, new_record)
            return new_record
        else:
            record_id = self.db.get_next_id(self.table_name)
            new_record["id"] = record_id
            self.db.insert(self.table_name, record_id, new_record)
            self.db.increment_counter(self.table_name)
            return new_record

    def update(self, record_id: int, field_changes: dict) -> dict | None:
        """Apply field_changes to the record matching record_id."""
        data = self.db._data[self.table_name]
        if isinstance(data, list):
            for i, r in enumerate(data):
                if r.get("id") == record_id:
                    r.update(field_changes)
                    self.db._persist()
                    return r
            return None
        return self.db.update(self.table_name, record_id, field_changes)

    def delete(self, record_id: int) -> bool:
        """Remove the record with the given id."""
        data = self.db._data[self.table_name]
        if isinstance(data, list):
            old_len = len(data)
            new_list = [r for r in data if r.get("id") != record_id]
            self.db.replace_list(self.table_name, new_list)
            return len(new_list) < old_len
        return self.db.delete(self.table_name, record_id)

