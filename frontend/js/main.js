const API_BASE = "http://127.0.0.1:8000";

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/statistics/`);
        const data = await res.json();
        
        const container = document.getElementById('stats-container');
        container.innerHTML = `
            <div class="col-md-3">
                <div class="card bg-primary text-white p-3 text-center">
                    <h5>Total Transactions</h5>
                    <h3>${data.total_transactions}</h3>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white p-3 text-center">
                    <h5>Legitimate</h5>
                    <h3>${data.legitimate_transactions}</h3>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-danger text-white p-3 text-center">
                    <h5>Predicted Fraud</h5>
                    <h3>${data.fraudulent_transactions}</h3>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-dark p-3 text-center">
                    <h5>Fraud Rate</h5>
                    <h3>${data.fraud_percentage}%</h3>
                </div>
            </div>
        `;
    } catch (e) {
        console.error("Error fetching stats", e);
    }
}

async function fetchHistory() {
    try {
        const res = await fetch(`${API_BASE}/transactions/?limit=10`);
        const data = await res.json();
        
        const tbody = document.querySelector('#history-table tbody');
        tbody.innerHTML = "";
        
        data.forEach(tx => {
            let riskClass = "risk-low";
            if (tx.risk_level === "HIGH") riskClass = "risk-high";
            if (tx.risk_level === "MEDIUM") riskClass = "risk-medium";
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${tx.id}</td>
                <td>$${tx.amount.toFixed(2)}</td>
                <td><strong>${tx.prediction}</strong></td>
                <td>${(tx.fraud_probability * 100).toFixed(2)}%</td>
                <td class="${riskClass}">${tx.risk_level}</td>
                <td>${new Date(tx.timestamp).toLocaleString()}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error fetching history", e);
    }
}

let currentDemoFeatures = null;

async function fetchDemo(type) {
    try {
        const response = await fetch(`${API_BASE}/demo/transaction?type=${type}`);
        if (response.ok) {
            const data = await response.json();
            currentDemoFeatures = data.features;
            
            // Show details
            document.getElementById('demo-details').style.display = 'block';
            document.getElementById('demo-label').textContent = data.type;
            
            // Format features for display
            const featureStr = Object.entries(data.features)
                .map(([k, v]) => `${k}: ${v.toFixed(4)}`)
                .join(', ');
            document.getElementById('demo-features-text').textContent = featureStr;
            
            // Enable predict button
            document.getElementById('predict-btn').disabled = false;
            
            // Hide previous results
            document.getElementById('prediction-result').classList.add('d-none');
        }
    } catch (error) {
        console.error('Error fetching demo:', error);
        alert('Failed to fetch demo transaction');
    }
}

async function submitDemo() {
    if (!currentDemoFeatures) return;
    
    try {
        const payload = { features: currentDemoFeatures };
        
        const res = await fetch(`${API_BASE}/predict/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        const result = await res.json();
        
        const resultDiv = document.getElementById('prediction-result');
        resultDiv.classList.remove('d-none');
        
        document.getElementById('res-pred').textContent = result.prediction;
        document.getElementById('res-pred').className = result.prediction === "FRAUD" ? "badge bg-danger fs-6" : "badge bg-success fs-6";
        
        document.getElementById('res-prob').textContent = (result.fraud_probability * 100).toFixed(2);
        document.getElementById('res-thresh').textContent = (result.decision_threshold * 100).toFixed(2);
        document.getElementById('res-level').textContent = result.risk_level;
        
        if (result.model) {
            document.getElementById('res-model').textContent = result.model;
            document.getElementById('res-feat-count').textContent = result.feature_count;
        }
        
        let riskClass = "risk-low";
        if (result.risk_level === "HIGH") riskClass = "risk-high";
        if (result.risk_level === "MEDIUM") riskClass = "risk-medium";
        document.getElementById('res-level').className = riskClass;
        
        // Refresh dashboard
        fetchStats();
        fetchHistory();
        
    } catch (e) {
        alert("Error making prediction: " + e.message);
    }
}

// Initial load
fetchStats();
fetchHistory();
