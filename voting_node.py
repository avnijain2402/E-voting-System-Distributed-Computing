from encryption import EncryptionModule

class VotingNode:
    """
    Represents an independent node in the distributed network structure.
    Nodes independently verify arriving transactions before they are allowed into the ledger.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.status = "Active"
        self.votes_processed = 0
        self.last_action = "Node Started"
        
    def toggle_status(self):
        if self.status == "Active":
            self.status = "Offline"
            self.last_action = "Node failed / taken offline"
        else:
            self.status = "Active"
            self.last_action = "Node recovered / back online"

    def validate_vote(self, transaction: dict) -> tuple:
        """
        Returns (is_valid, log_message)
        """
        if self.status != "Active":
            return False, f"[{self.node_id}] is offline. Cannot process."

        required_fields = ["voter_id_hash", "encrypted_vote", "timestamp", "signature", "public_key"]
        for field in required_fields:
            if field not in transaction:
                self.last_action = f"Validation Failed: Missing {field}"
                return False, f"[{self.node_id}] Validation Error: missing {field}."

        # Verify PKI signature
        payload_to_verify = f"{transaction['voter_id_hash']}:{transaction['encrypted_vote']}:{transaction['timestamp']}"
        is_valid_sig = EncryptionModule.verify_signature_pki(
            transaction['public_key'], 
            payload_to_verify, 
            transaction['signature']
        )

        if not is_valid_sig:
            self.last_action = "Validation Failed: Invalid PKI Signature"
            return False, f"[{self.node_id}] Validation Error: Invalid PKI Signature."

        self.votes_processed += 1
        self.last_action = f"Verified vote ID: {transaction['signature'][:8]}"
        return True, f"[{self.node_id}] verified vote {transaction['signature'][:8]} successfully."

    def get_status(self) -> dict:
        return {
            "node_id": self.node_id,
            "status": self.status,
            "votes_processed": self.votes_processed,
            "last_action": self.last_action
        }
