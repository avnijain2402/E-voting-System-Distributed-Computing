import time
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

from authentication import AuthenticationModule
from encryption import EncryptionModule
from ledger import DistributedLedger
from consensus import ConsensusEngine

app = Flask(__name__)
app.secret_key = "DISTRIBUTED_E_VOTING_SECRET_KEY"

# Initialize our simulated system components.
auth_module = AuthenticationModule()
shared_ledger = DistributedLedger()
consensus_engine = ConsensusEngine(num_nodes=3)

CANDIDATES = [
    {"id": "c1", "name": "Candidate A", "party": "Party Alpha"},
    {"id": "c2", "name": "Candidate B", "party": "Party Beta"},
    {"id": "c3", "name": "Candidate C", "party": "Party Gamma"}
]

@app.route("/")
def index():
    if "voter_id" in session:
        return redirect(url_for("vote"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name")
        voter_id = request.form.get("voter_id")
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not all([name, voter_id, email, password]):
            error = "All fields are required."
        else:
            voter_id = voter_id.strip().upper()
            success, message = auth_module.register_voter(name, voter_id, email, password)
            if success:
                return redirect(url_for("login", msg="Registration successful! Please login."))
            else:
                error = message
                
    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    msg = request.args.get("msg")
    if request.method == "POST":
        voter_id = request.form.get("voter_id")
        password = request.form.get("password")
        voter_id = voter_id.strip().upper()

        is_valid, message = auth_module.authenticate(voter_id, password)
        if is_valid:
            session["voter_id"] = voter_id
            
            # Generate token and store in session
            token = secrets.token_hex(4).upper()
            session["voting_token"] = token
            
            return render_template("token_display.html", token=token)
        else:
            error = message
            
    return render_template("login.html", error=error, msg=msg)

@app.route("/logout")
def logout():
    session.pop("voter_id", None)
    return redirect(url_for("login"))

@app.route("/vote", methods=["GET", "POST"])
def vote():
    if "voter_id" not in session:
        return redirect(url_for("login"))

    voter_id = session["voter_id"]
    
    # Check if they have voted
    voter = auth_module.get_voter(voter_id)
    if not voter or voter.get("has_voted"):
        return render_template("results.html", message="You have already cast your vote! Thank you.")

    if request.method == "POST":
        chosen_candidate = request.form.get("candidate")
        submitted_token = request.form.get("voting_token")
        
        if submitted_token != session.get("voting_token"):
            return render_template("vote.html", candidates=CANDIDATES, error="Invalid voting token. Please try logging in again.")

        if not chosen_candidate:
            return render_template("vote.html", candidates=CANDIDATES, error="Please select a candidate.")

        # Cryptography
        hashed_id = EncryptionModule.hash_voter_id(voter_id)
        encrypted_vote = EncryptionModule.encrypt_vote(chosen_candidate)
        timestamp = time.time()
        
        # PKI signing
        private_key = voter.get("private_key")
        public_key = voter.get("public_key")
        
        payload_to_sign = f"{hashed_id}:{encrypted_vote}:{timestamp}"
        signature = EncryptionModule.sign_transaction_pki(private_key, payload_to_sign)
        
        transaction = {
            "voter_id_hash": hashed_id,
            "encrypted_vote": encrypted_vote,
            "timestamp": timestamp,
            "signature": signature,
            "public_key": public_key
        }

        # Send vote to distributed nodes
        # Simulate network broadcast to consensus engine
        consensus_reached, approving_nodes = consensus_engine.reach_consensus(transaction)
        
        if consensus_reached:
            # Add transaction block to ledger
            shared_ledger.add_block(transaction, approving_nodes)
            consensus_engine.log_event(f"Vote stored in ledger block. Sig: {signature[:8]}")
            
            auth_module.mark_voted(voter_id)
            # Remove token so it can't be reused
            session.pop("voting_token", None)
            return redirect(url_for("results", success="Your vote was successfully verified and recorded by the network."))
        else:
            consensus_engine.log_event(f"Vote rejected: node consensus failed.")
            error = "Network consensus failed. Your vote was rejected by the nodes."
            return render_template("vote.html", candidates=CANDIDATES, error=error)

    return render_template("vote.html", candidates=CANDIDATES)

@app.route("/results")
def results():
    success_msg = request.args.get("success")
    return render_template("results.html", message=success_msg)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# -----------------
# API Endpoints
# -----------------
@app.route("/api/stats", methods=["GET"])
def api_stats():
    total_registered = auth_module.get_total_registered()
    current_tally = shared_ledger.tally_results()
    total_votes = sum(current_tally.values())
    turnout = round((total_votes / total_registered * 100), 1) if total_registered > 0 else 0
    return jsonify({
        "total_registered_voters": total_registered,
        "total_votes_cast": total_votes,
        "voter_turnout": turnout
    })

@app.route("/api/nodes", methods=["GET"])
def api_nodes():
    statuses = consensus_engine.get_node_statuses()
    nodes = []
    for s in statuses:
        nodes.append({
            "id": s["node_id"],
            "status": s["status"],
            "votes_processed": s["votes_processed"],
            "last_action": s["last_action"]
        })
    return jsonify({"nodes": nodes})

@app.route("/api/ledger", methods=["GET"])
def api_ledger():
    try:
        import os, json
        if os.path.exists("ledger.json"):
            with open("ledger.json", "r") as f:
                data = json.load(f)
                blocks = []
                if isinstance(data, list):
                    blocks = [item for item in data if "block_id" in item]
                elif isinstance(data, dict) and "chain" in data:
                    blocks = [item for item in data["chain"] if "block_id" in item]
                return jsonify({"chain": blocks})
        return jsonify({"chain": []})
    except Exception:
        return jsonify({"chain": []})

@app.route("/api/activity", methods=["GET"])
def api_activity():
    return jsonify(consensus_engine.get_recent_logs())

@app.route("/api/votes", methods=["GET"])
def api_votes():
    return jsonify(shared_ledger.tally_results())

@app.route("/api/toggle_node", methods=["POST"])
def toggle_node():
    data = request.get_json()
    node_id = data.get("node_id")
    if node_id:
        success = consensus_engine.simulate_failure(node_id)
        if success:
            return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
