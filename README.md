# Distributed E-Voting Web System

A fully-fledged Flask web application demonstrating a secure, distributed e-voting mechanism. 

## Features
- **Sleek Glassmorphic UI**: Beautiful, responsive, modern web interface.
- **Client Authentication**: Ensures registered voters can only cast a single ballot securely.
- **Vote Encryption**: Votes are encrypted and digitally signed (simulated using SHA-256 and Base64) to ensure anonymity and payload immutability.
- **Distributed Consensus**: A simulation of three independent backend nodes. When a vote is cast, it must be validated by a majority of these nodes before it is allowed into the ledger.
- **Tamper-Resistant Ledger**: Votes are stored in a persistent `ledger.json` file.
- **Live Admin Dashboard**: A real-time monitoring dashboard leveraging `Chart.js` to visualize live voting tallies, view current node health status, and read recent ledger transactions.

## Project Structure
- `app.py`: The main Flask routing server, handling HTTP requests and gluing components together.
- `authentication.py`: Validates voters against a database (`voters.json`).
- `encryption.py`: Mocks the cryptographic procedures necessary for anonymity.
- `voting_node.py` & `consensus.py`: The distributed logic that validates transactions.
- `ledger.py`: Handles appending and reading from the persistent data store.
- `templates/`: HTML structures (`login.html`, `vote.html`, `dashboard.html`, `results.html`).
- `static/`: Contains the styling `style.css` and the frontend polling logic `dashboard.js`.

## How to Run

1. Have Python installed.
2. Open your terminal in this directory (`evoting_system`).
3. If you don't have Flask, install it:
   ```bash
   pip install Flask
   ```
4. Start the server:
   ```bash
   python app.py
   ```
5. Open your web browser and navigate to `http://127.0.0.1:5000`.

### Demo Access
- You can log in to the voter portal using standard mock IDs:
  - `VOTER123`
  - `VOTER456`
  - `VOTER789`
- Once logged in, choose a candidate and watch the consensus nodes process your vote!
- To view the real-time election results, navigate to the `Dashboard` via the navigation bar!

---

## 🎯 Future Enhancements & Future Scope

### 1. Admin Portal
* **Current System**: Users can vote and view results.
* **Future Improvement**: A separate Admin Login where the administrator can monitor all voting activities, view the blockchain ledger, inspect node status (Node1, Node2, Node3), manage elections and candidates, and generate voting reports.
* *One-line for PPT:*
  > "A dedicated admin dashboard can be added for monitoring elections, node activity, and voting results."

### 2. Multi-Year Election Support
* **Current System**: Designed for a single election cycle.
* **Future Improvement**: Support for multiple elections and storing election history, allowing new batches of users to vote every year, archiving old election data, and comparing results across years. Each election cycle (e.g., 2025, 2026, 2027) will have separate candidates, voter lists, and a separate blockchain ledger.
* *One-line for PPT:*
  > "The system can be extended to support multiple election cycles with separate voter records and blockchain ledgers."

### 3. Real Distributed Deployment
* **Current System**: Node simulation (Node1, Node2, Node3) runs locally on a single machine.
* **Future Improvement**: True physical distribution of voting nodes on separate servers across different geographic regions (e.g., Delhi, Mumbai, Bangalore) to ensure physical fault tolerance.

### 4. Advanced Authentication
* **Current System**: Simple password-based authentication.
* **Future Improvement**: Adding Aadhaar verification (for academic discussion), biometric authentication, OTP verification, or face recognition to guarantee one-voter-one-vote enforcement.

### 5. Cloud Deployment
* **Current System**: Hosted locally.
* **Future Improvement**: Deployment on AWS, Google Cloud, or Azure to achieve horizontal scalability for municipal or national-level voting.

---

## 🔥 Best 5 Points for PPT

### Future Scope
1. **Dedicated Admin Dashboard**: For complete election and node cluster integrity monitoring.
2. **Multi-Year Cycle Support**: Running recurring election cycles and historical comparison.
3. **Physical Node Distribution**: Deployment on real, geographically distributed servers.
4. **MFA & Advanced Authentication**: Elevating voter verification using biometric/OTP systems.
5. **Cloud-Based Scalability**: Deploying to hyperscalers (AWS/GCP/Azure) to handle massive loads.

### Conclusion
> **"The proposed system demonstrates secure distributed voting and can be extended with admin controls, multi-year elections, and real-world distributed deployment."**

