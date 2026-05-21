import json
import os
import hashlib
from encryption import EncryptionModule

class AuthenticationModule:
    """
    Handles voter registration and authentication to ensure one vote per voter.
    Uses a simple JSON file to persist voter status.
    """
    def __init__(self, db_file="voters.json"):
        self.db_file = db_file
        self.voters = self._load_voters()
        
    def _load_voters(self) -> dict:
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    data = json.load(f)
                    # Support legacy array format or dict format
                    if "voters" in data and isinstance(data["voters"], list):
                        # Convert array format to dict format for easier lookup if needed, 
                        # but user specified Array format: {"voters": [{"name", "voter_id", "email", "password", "has_voted"}]}
                        return data
                    return {"voters": []}
            except json.JSONDecodeError:
                pass
        return {"voters": []}

    def _save_voters(self):
        with open(self.db_file, "w") as f:
            json.dump(self.voters, f, indent=4)

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def get_voter(self, voter_id: str):
        for v in self.voters["voters"]:
            if v["voter_id"] == voter_id:
                return v
        return None

    def register_voter(self, name: str, voter_id: str, email: str, password: str) -> tuple:
        """Returns (success_bool, message)"""
        if self.get_voter(voter_id):
            return False, "Voter ID already registered."
            
        pub_key, priv_key = EncryptionModule.generate_key_pair()
            
        new_voter = {
            "name": name,
            "voter_id": voter_id,
            "email": email,
            "password": self.hash_password(password),
            "public_key": pub_key,
            "private_key": priv_key,
            "has_voted": False
        }
        
        self.voters["voters"].append(new_voter)
        self._save_voters()
        return True, "Registration successful."

    def authenticate(self, voter_id: str, password: str) -> tuple:
        """Returns (success_bool, message)"""
        voter = self.get_voter(voter_id)
        if not voter:
            return False, "Unregistered Voter ID."
            
        if voter["password"] != self.hash_password(password):
            return False, "Incorrect password."
            
        if voter["has_voted"]:
            return False, "This voter has already cast a ballot."
            
        return True, "Authenticated successfully."

    def mark_voted(self, voter_id: str):
        """Marks the voter as having voted and saves to DB."""
        for v in self.voters["voters"]:
            if v["voter_id"] == voter_id:
                v["has_voted"] = True
                break
        self._save_voters()
        
    def get_total_registered(self) -> int:
        return len(self.voters["voters"])
