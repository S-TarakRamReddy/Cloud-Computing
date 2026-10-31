const API_BASE = "";

function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
}

function riskClassFor(level) {
    if (level === "HIGH") return "risk-high";
    if (level === "MEDIUM") return "risk-medium";
    return "risk-low";
}

async function apiJson(url, options) {
    const res = await fetch(url, options);
    let body = null;
    try { body = await res.json(); } catch (_) { /* non-JSON error body */ }
    if (!res.ok) {
        const detail = body && body.detail;
        throw new Error(typeof detail === "string" ? detail : `Request failed (${res.status})`);
    }
    return body;
}

function showError(message) {
    const box = document.getElementById('error-banner');
    box.textContent = message;
    box.classList.remove('d-none');
}

function clearError() {
    document.getElementById('error-banner').classList.add('d-none');
}

function statCard(colorClasses, label, value) {
    const col = el('div', 'col-6 col-md-3 mb-3 mb-md-0');
    const card = el('div', `card ${colorClasses} p-3 text-center`);
    card.append(el('h5', null, label), el('h3', null, value));
    col.appendChild(card);
    return col;
}

async function fetchStats() {
    try {
        const data = await apiJson(`${API_BASE}/statistics/`);
        const container = document.getElementById('stats-container');
        container.replaceChildren(
            statCard('bg-primary text-white', 'Total Transactions', data.total_transactions),
            statCard('bg-success text-white', 'Legitimate', data.legitimate_transactions),
            statCard('bg-danger text-white', 'Predicted Fraud', data.fraudulent_transactions),
            statCard('bg-warning text-dark', 'Fraud Rate', `${data.fraud_percentage}%`)
        );
    } catch (e) {
        console.error("Error fetching stats", e);
        showError("Could not load statistics: " + e.message);
    }
}

async function fetchHistory() {
    try {
        const data = await apiJson(`${API_BASE}/transactions/?limit=10`);
        const tbody = document.querySelector('#history-table tbody');
        tbody.replaceChildren();

        if (data.length === 0) {
            const tr = el('tr');
            const td = el('td', 'text-center text-muted', 'No transactions yet. Run a prediction to get started.');
            td.colSpan = 6;
            tr.appendChild(td);
            tbody.appendChild(tr);
            return;
        }

        data.forEach(tx => {
            const tr = el('tr');
            const pred = el('td');
            pred.appendChild(el('strong', null, tx.prediction));
            tr.append(
                el('td', null, tx.id),
                el('td', null, `\u20AC${tx.amount.toFixed(2)}`),
                pred,
                el('td', null, `${(tx.fraud_probability * 100).toFixed(2)}%`),
                el('td', riskClassFor(tx.risk_level), tx.risk_level),
                el('td', null, new Date(tx.timestamp).toLocaleString())
            );
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error fetching history", e);
        showError("Could not load recent transactions: " + e.message);
    }
}

let currentDemoFeatures = null;

function setBusy(button, busy, idleLabel) {
    button.disabled = busy;
    button.textContent = busy ? "Working..." : idleLabel;
}

async function fetchDemo(type) {
    clearError();
    try {
        const data = await apiJson(`${API_BASE}/demo/transaction?type=${encodeURIComponent(type)}`);
        currentDemoFeatures = data.features;

        document.getElementById('demo-details').style.display = 'block';
        document.getElementById('demo-label').textContent = data.type;

        const featureStr = Object.entries(data.features)
            .map(([k, v]) => `${k}: ${v.toFixed(4)}`)
            .join(', ');
        document.getElementById('demo-features-text').textContent = featureStr;

        document.getElementById('predict-btn').disabled = false;
        document.getElementById('prediction-result').classList.add('d-none');
    } catch (error) {
        console.error('Error fetching demo:', error);
        showError('Failed to fetch demo transaction: ' + error.message);
    }
}

async function submitDemo() {
    if (!currentDemoFeatures) return;
    clearError();

    const button = document.getElementById('predict-btn');
    setBusy(button, true, "Predict Fraud Risk");
    try {
        const result = await apiJson(`${API_BASE}/predict/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ features: currentDemoFeatures })
        });

        document.getElementById('prediction-result').classList.remove('d-none');

        const pred = document.getElementById('res-pred');
        pred.textContent = result.prediction;
        pred.className = result.prediction === "FRAUD" ? "badge bg-danger fs-6" : "badge bg-success fs-6";

        document.getElementById('res-prob').textContent = (result.fraud_probability * 100).toFixed(2);
        document.getElementById('res-thresh').textContent = (result.decision_threshold * 100).toFixed(2);

        const level = document.getElementById('res-level');
        level.textContent = result.risk_level;
        level.className = riskClassFor(result.risk_level);

        document.getElementById('res-model').textContent = result.model;
        document.getElementById('res-feat-count').textContent = result.feature_count;

        fetchStats();
        fetchHistory();
    } catch (e) {
        showError("Error making prediction: " + e.message);
    } finally {
        setBusy(button, false, "Predict Fraud Risk");
    }
}

fetchStats();
fetchHistory();
