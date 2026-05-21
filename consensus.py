from voting_node import VotingNode
import time

class ConsensusEngine:
    """
    Manages the distributed nodes and ensures a transaction is only committed
    if a majority of nodes agree it is valid.
    """
    def __init__(self, num_nodes=3):
        self.nodes = [VotingNode(f"Node{i+1}") for i in range(num_nodes)]
        self.logs = []  # In-memory unified system activity log

    def log_event(self, message: str):
        timestamp = time.strftime('%H:%M:%S', time.localtime())
        self.logs.append(f"[{timestamp}] {message}")
        # Keep last 10 logs
        if len(self.logs) > 10:
            self.logs.pop(0)

    def reach_consensus(self, transaction: dict) -> tuple:
        """
        Returns a tuple: (consensus_reached_bool, list_of_approving_nodes)
        """
        self.log_event(f"System: Received vote {transaction['signature'][:8]}")
        
        approving_nodes = []
        for node in self.nodes:
            self.log_event(f"System: Sending vote to {node.node_id}...")
            
            if node.status != "Active":
                self.log_event(f"{node.node_id} is offline. Skipped.")
                continue
                
            is_valid, log_msg = node.validate_vote(transaction)
            if is_valid:
                approving_nodes.append(node.node_id)
                self.log_event(f"{node.node_id} verified vote.")
                
        total_active_nodes = len([n for n in self.nodes if n.status == "Active"])
        total_system_nodes = len(self.nodes)
        approvals = len(approving_nodes)
        
        # Require majority (> 50%) of ALL nodes for consensus, even if some offline
        if approvals > total_system_nodes / 2:
            self.log_event(f"Consensus Reached: {approvals}/{total_system_nodes} nodes approved.")
            return True, approving_nodes
        else:
            self.log_event(f"Consensus FAILED: Only {approvals}/{total_system_nodes} nodes approved.")
            return False, approving_nodes

    def get_node_statuses(self) -> list:
        return [node.get_status() for node in self.nodes]
        
    def get_recent_logs(self) -> list:
        return self.logs
        
    def simulate_failure(self, node_id: str) -> bool:
        for node in self.nodes:
            if node.node_id == node_id:
                node.toggle_status()
                self.log_event(f"Admin triggered status change on {node.node_id} -> {node.status}")
                return True
        return False
