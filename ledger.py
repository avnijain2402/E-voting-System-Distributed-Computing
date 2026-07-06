import json
import os
import hashlib
import time
from encryption import EncryptionModule

class DistributedLedger:
    """
    Simulates a tamper-resistant distributed ledger (Blockchain).
    Persists blocks to a JSON file.
    """
    def __init__(self, ledger_file="ledger.json"):
        self.ledger_file = ledger_file
        self.blocks = []
        self._load_ledger()

    def _load_ledger(self):
        """Loads existing ledger data on startup."""
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, "r") as f:
                    self.blocks = json.load(f)
            except json.JSONDecodeError:
                self.blocks = []
        else:
            self._save_ledger()

    def _save_ledger(self):
        """Commits the current chain to disk."""
        with open(self.ledger_file, "w") as f:
            json.dump(self.blocks, f, indent=4)

    def add_block(self, transaction: dict, verified_nodes: list):
        """Creates a new block and appends it to the chain."""
        block_id = len(self.blocks) + 1
        timestamp = time.time()
        
        previous_hash = "0"
        if len(self.blocks) > 0:
            previous_hash = self.blocks[-1].get("block_hash", "0")
            
        vote_data_str = json.dumps(transaction, sort_keys=True)
        vote_hash = hashlib.sha256(vote_data_str.encode('utf-8')).hexdigest()
        
        block_content = f"{block_id}{previous_hash}{vote_hash}{timestamp}"
        block_hash = hashlib.sha256(block_content.encode('utf-8')).hexdigest()
        
        new_block = {
            "block_id": block_id,
            "previous_hash": previous_hash,
            "vote_hash": vote_hash,
            "timestamp": timestamp,
            "verified_nodes": verified_nodes,
            "block_hash": block_hash,
            "transaction": transaction
        }
        
        self.blocks.append(new_block)
        self._save_ledger()

    def get_all_transactions(self) -> list:
        # For backward compatibility with tally_results and app.py which expect transactions
        return [b.get("transaction", b) for b in self.blocks]
        
    def get_all_blocks(self) -> list:
        return self.blocks

    def tally_results(self, election_id: str = None) -> dict:
        """
        Iterates over the ledger blocks, decrypts votes, and tallies the current results.
        If election_id is provided, filters to only count blocks belonging to that election.
        """
        results = {}
        for block in self.blocks:
            tx = block.get("transaction", block)
            tx_election_id = tx.get("election_id", block.get("election_id", "LEGACY_ELECTION"))
            if election_id and tx_election_id != election_id:
                continue
            encrypted_vote = tx.get("encrypted_vote")
            if encrypted_vote:
                decrypted_candidate = EncryptionModule.decrypt_vote(encrypted_vote)
                results[decrypted_candidate] = results.get(decrypted_candidate, 0) + 1
        return results
