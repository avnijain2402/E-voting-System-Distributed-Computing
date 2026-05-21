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
