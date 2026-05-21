let voteChartInstance = null;
let lastNodeData = [];

function initChart() {
    const ctx = document.getElementById('voteChart').getContext('2d');
    voteChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Votes Cast',
                data: [],
                backgroundColor: [
                    'rgba(56, 189, 248, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(167, 139, 250, 0.7)',
                    'rgba(251, 146, 60, 0.7)'
                ],
                borderColor: [
                    'rgb(56, 189, 248)',
                    'rgb(16, 185, 129)',
                    'rgb(167, 139, 250)',
                    'rgb(251, 146, 60)'
                ],
                borderWidth: 2,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, ticks: { color: '#94a3b8', stepSize: 1 } },
                x: { ticks: { color: '#e2e8f0' } }
            }
        }
    });
}

function renderBlockchain(chain) {
    const container = document.getElementById("blocks-container");
    container.innerHTML = "";

    if (!chain || chain.length === 0) {
        container.innerHTML = "<p style='color:white;'>No blocks available</p>";
        return;
    }

    // Sort blocks properly
    chain.sort((a, b) => a.block_id - b.block_id);

    chain.forEach((block, index) => {

        // Create block card
        const card = document.createElement("div");
        card.style.display = "inline-block";
        card.style.padding = "15px";
        card.style.margin = "10px";
        card.style.background = "#1a1a2e";
        card.style.border = "2px solid #00ffcc";
        card.style.borderRadius = "10px";
        card.style.color = "white";
        card.style.minWidth = "180px";

        card.innerHTML = `
            <b>Block ${block.block_id}</b><br>
            <small>Hash:</small><br>${block.block_hash.substring(0, 12)}...<br>
            <small>Prev:</small><br>${block.previous_hash.substring(0, 12)}...
        `;

        container.appendChild(card);

        // Add arrow between blocks
        if (index < chain.length - 1) {
            const arrow = document.createElement("span");
            arrow.innerHTML = " → ";
            arrow.style.color = "#00ffcc";
            arrow.style.fontSize = "20px";
            container.appendChild(arrow);
        }
    });
}

function renderLedgerTable(chain) {
    const ledgerBody = document.getElementById('ledger-body');
    ledgerBody.innerHTML = '';

    // Display newest blocks at the top of the table
    const tableChain = [...chain].reverse();
    tableChain.forEach(row => {
        const tr = document.createElement('tr');
        const nodesStr = Array.isArray(row.verified_nodes) ? row.verified_nodes.join(', ') : row.verified_nodes;
        tr.innerHTML = `
            <td>${row.block_id}</td>
            <td class="font-mono text-accent">${row.block_hash.substring(0, 8)}...</td>
            <td class="font-mono text-muted">${row.previous_hash === '0' ? '0' : row.previous_hash.substring(0, 8) + '...'}</td>
            <td class="font-mono">${row.vote_hash.substring(0, 8)}...</td>
            <td><span class="badge badge-success">${nodesStr}</span></td>
            <td class="text-muted">${row.timestamp}</td>
        `;
        ledgerBody.appendChild(tr);
    });
}

function updateDashboard() {
    // 1. Fetch Stats
    fetch("/api/stats")
        .then(res => res.json())
        .then(data => {
            document.getElementById('stat-registered').innerText = data.total_registered_voters;
            document.getElementById('stat-votes').innerText = data.total_votes_cast;
            document.getElementById('stat-turnout').innerText = data.voter_turnout + "%";
        })
        .catch(e => console.error("Error fetching stats:", e));

    // 2. Fetch Nodes
    fetch("/api/nodes")
        .then(res => res.json())
        .then(data => {
            const nodesContainer = document.getElementById('nodes-container');
            nodesContainer.innerHTML = '';
            lastNodeData = data.nodes;
            data.nodes.forEach(node => {
                const isActive = node.status === 'Active';
                const nodeEl = document.createElement('div');
                nodeEl.className = `node-card ${isActive ? 'active-node' : 'offline-node'}`;
                nodeEl.innerHTML = `
                    <div class="node-header">
                        <span class="status-indicator"></span>
                        <strong>${node.id}</strong>
                    </div>
                    <p>Status: <span>${node.status}</span></p>
                    <p>Votes Processed: ${node.votes_processed}</p>
                    <hr style="border:0;border-top:1px solid rgba(255,255,255,0.1); margin:10px 0;">
                    <small style="color:#94a3b8;">${node.last_action}</small>
                    <button class="toggle-btn" onclick="toggleNode('${node.id}')">Toggle Status</button>
                `;
                nodesContainer.appendChild(nodeEl);
            });
        })
        .catch(e => console.error("Error fetching nodes:", e));

    // 3. Fetch Ledger
    fetch("/api/ledger")
        .then(res => res.json())
        .then(data => {
            console.log("LEDGER DATA:", data);
            const chain = data.chain || [];
            renderBlockchain(chain);
            renderLedgerTable(chain);
        })
        .catch(e => console.error("Error fetching ledger:", e));

    // 4. Fetch Activity Logs
    fetch("/api/activity")
        .then(res => res.json())
        .then(data => {
            const logWindow = document.getElementById('activity-log');
            logWindow.innerHTML = '';
            data.forEach(log => {
                const p = document.createElement('p');
                p.className = 'log-line';
                p.innerHTML = log.replace(/System|Node\d|Consensus/g, match => `<strong style="color:#a78bfa;">${match}</strong>`);
                logWindow.appendChild(p);
            });
        })
        .catch(e => console.error("Error fetching activity:", e));

    // 5. Fetch Votes
    fetch("/api/votes")
        .then(res => res.json())
        .then(data => {
            if (voteChartInstance) {
                voteChartInstance.data.labels = Object.keys(data);
                voteChartInstance.data.datasets[0].data = Object.values(data);
                voteChartInstance.update();
            }
        })
        .catch(e => console.error("Error fetching votes:", e));
}

async function toggleNode(nodeId) {
    await fetch('/api/toggle_node', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ node_id: nodeId })
    });
    updateDashboard();
}

function simulateFailure() {
    // Pick a random node and toggle it
    if (lastNodeData.length > 0) {
        const randomNode = lastNodeData[Math.floor(Math.random() * lastNodeData.length)];
        toggleNode(randomNode.id);
    }
}

// Init and Poll every 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    updateDashboard();
    setInterval(updateDashboard, 5000);
});
