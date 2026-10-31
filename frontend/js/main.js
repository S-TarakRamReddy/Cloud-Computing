const API_BASE = "";
const WHATIF_FEATURES = 4;   // sliders for the most influential features
const FEATURE_COUNT = 29;

// ---------- helpers ----------
const $ = (id) => document.getElementById(id);

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
    const box = $('error-banner');
    box.textContent = message;
    box.classList.remove('d-none');
}

function clearError() { $('error-banner').classList.add('d-none'); }

const pct = (x, digits = 2) => (x * 100).toFixed(digits);

// ---------- state ----------
const state = {
    original: null,      // features as loaded
    current: null,       // features after what-if edits
    label: null,         // dataset label (FRAUD / LEGITIMATE / null for pasted data)
    card: null,          // model card from /model-card
    scenario: null,
};

// ---------- dashboard: stats + history ----------
function statCard(colorClasses, label, value) {
    const col = el('div', 'col-6 col-md-3 mb-3 mb-md-0');
    const card = el('div', `card ${colorClasses} p-3 text-center stat-card`);
    card.append(el('h6', 'mb-1', label), el('h3', 'mb-0', value));
    col.appendChild(card);
    return col;
}

async function fetchStats() {
    try {
        const data = await apiJson(`${API_BASE}/statistics/`);
        $('stats-container').replaceChildren(
            statCard('bg-primary text-white', 'Analysed', data.total_transactions),
            statCard('bg-success text-white', 'Legitimate', data.legitimate_transactions),
            statCard('bg-danger text-white', 'Flagged as fraud', data.fraudulent_transactions),
            statCard('bg-warning text-dark', 'Flag rate (demo only)', `${data.fraud_percentage}%`)
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
            const td = el('td', 'text-center text-muted', 'No transactions yet. Analyse one to get started.');
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
                el('td', null, `€${tx.amount.toFixed(2)}`),
                pred,
                el('td', null, `${pct(tx.fraud_probability)}%`),
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

function refreshDashboard() { fetchStats(); fetchHistory(); }

// ---------- model card: importance + metrics ----------
function renderImportance(card) {
    const entries = Object.entries(card.feature_importance).sort((a, b) => b[1] - a[1]).slice(0, 10);
    const max = entries[0][1];
    $('importance').replaceChildren(...entries.map(([name, v]) => {
        const row = el('div', 'imp-row');
        const track = el('div');
        const bar = el('div', 'imp-bar');
        bar.style.width = `${(v / max) * 100}%`;
        track.appendChild(bar);
        row.append(el('span', 'fw-semibold', name), track, el('span', 'text-end text-muted', `${pct(v, 1)}%`));
        return row;
    }));
}

function renderCard(card) {
    const t = card.test_set, c = card.confusion_matrix, m = card.metrics;
    $('card-intro').textContent =
        `Measured on ${t.rows.toLocaleString()} transactions the model never saw, ` +
        `of which only ${t.fraud_cases} were fraud.`;

    const rows = [
        ["Precision (flags that were real fraud)", m.precision],
        ["Recall (fraud cases caught)", m.recall],
        ["F1 (balance of the two)", m.f1],
        ["PR-AUC (ranking quality)", m.pr_auc],
        ["ROC-AUC", m.roc_auc],
    ];
    $('metrics-body').replaceChildren(...rows.map(([label, metric]) => {
        const tr = el('tr');
        const range = metric.ci95 ? `${pct(metric.ci95[0], 0)}% – ${pct(metric.ci95[1], 0)}%` : "–";
        tr.append(el('td', null, label), el('td', 'fw-semibold', `${pct(metric.value, 1)}%`), el('td', 'text-muted range-label', range));
        return tr;
    }));

    const cell = (value, label, cls) => {
        const col = el('div', 'col-6 col-md-3');
        const box = el('div', `border rounded p-2 ${cls}`);
        box.append(el('div', 'fs-5 fw-bold', value.toLocaleString()), el('div', 'text-muted', label));
        col.appendChild(box);
        return col;
    };
    $('confusion').replaceChildren(
        cell(c.tp, 'fraud caught', 'border-success'),
        cell(c.fn, 'fraud missed', 'border-danger'),
        cell(c.fp, 'false alarms', 'border-warning'),
        cell(c.tn, 'correctly cleared', 'border-secondary')
    );
    $('card-note').textContent =
        `*Ranges come from ${card.bootstrap.resamples.toLocaleString()} bootstrap resamples. With only ${t.fraud_cases} fraud cases, ` +
        `the true recall could plausibly be anywhere in that range, so quote it as a range rather than a single number.`;
}

async function loadModelCard() {
    try {
        state.card = await apiJson(`${API_BASE}/model-card`);
        renderImportance(state.card);
        renderCard(state.card);
    } catch (e) {
        console.error("Model card unavailable", e);
        $('card-intro').textContent = "Model evaluation details are not available.";
    }
}

// ---------- scenario selection ----------
function setActiveScenario(button) {
    document.querySelectorAll('.scenario').forEach(b => {
        const on = b === button;
        b.classList.toggle('active', on);
        b.setAttribute('aria-checked', on ? 'true' : 'false');
    });
}

function loadSample(features, label) {
    state.original = { ...features };
    state.current = { ...features };
    state.label = label;

    $('sample-info').classList.remove('d-none');
    const badge = $('demo-label');
    badge.textContent = label || "Your data (no label)";
    badge.className = "badge " + (label === "FRAUD" ? "bg-danger" : label === "LEGITIMATE" ? "bg-success" : "bg-secondary");
    $('demo-features-text').textContent = Object.entries(features)
        .map(([k, v]) => `${k}: ${Number(v).toFixed(4)}`).join(', ');

    buildWhatIf();
    $('predict-btn').disabled = false;
    runPrediction({ log: false });
}

async function selectScenario(button) {
    clearError();
    $('paste-box').classList.add('d-none');
    setActiveScenario(button);
    state.scenario = button.dataset.type;
    const honest = $('honest-mode').checked;
    try {
        const data = await apiJson(`${API_BASE}/demo/transaction?type=${encodeURIComponent(state.scenario)}&honest=${honest}`);
        loadSample(data.features, data.type);
    } catch (e) {
        console.error('Error fetching demo:', e);
        showError('Failed to fetch demo transaction: ' + e.message);
    }
}

function togglePaste() {
    setActiveScenario($('paste-toggle'));
    state.scenario = "paste";
    $('paste-box').classList.remove('d-none');
    $('paste-input').focus();
}

function loadPasted() {
    clearError();
    let parsed;
    try { parsed = JSON.parse($('paste-input').value); }
    catch (_) { showError("That is not valid JSON."); return; }
    if (parsed && typeof parsed.features === "object") parsed = parsed.features;
    const keys = parsed && typeof parsed === "object" ? Object.keys(parsed) : [];
    if (keys.length !== FEATURE_COUNT || !keys.every(k => Number.isFinite(Number(parsed[k])))) {
        showError(`Expected exactly ${FEATURE_COUNT} numeric features (V1–V28 and Amount); got ${keys.length}.`);
        return;
    }
    const clean = {};
    keys.forEach(k => { clean[k] = Number(parsed[k]); });
    loadSample(clean, null);
}

// ---------- what-if explorer ----------
function topFeatures() {
    const imp = state.card ? state.card.feature_importance : {};
    return Object.entries(imp)
        .filter(([name]) => name !== "Amount" && name in state.current)
        .sort((a, b) => b[1] - a[1])
        .slice(0, WHATIF_FEATURES)
        .map(([name]) => name);
}

let debounceTimer = null;
function scheduleLivePrediction() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => runPrediction({ log: false }), 250);
}

function buildWhatIf() {
    $('whatif-empty').classList.add('d-none');
    $('whatif-controls').classList.remove('d-none');

    $('amount-input').value = Number(state.current.Amount).toFixed(2);

    const box = $('sliders');
    box.replaceChildren();
    topFeatures().forEach(name => {
        const [lo, hi] = state.card.feature_ranges[name];
        const value = Number(state.current[name]);
        const min = Math.min(lo, value), max = Math.max(hi, value);

        const wrap = el('div', 'mb-3');
        const head = el('div', 'd-flex justify-content-between small');
        const readout = el('span', 'range-label text-muted', value.toFixed(2));
        const importance = state.card.feature_importance[name];
        head.append(el('label', 'fw-semibold', `${name} (${pct(importance, 0)}% of decision)`), readout);

        const input = el('input', 'form-range');
        input.type = "range";
        input.min = min; input.max = max; input.step = 0.05; input.value = value;
        input.id = `slider-${name}`;
        input.setAttribute('aria-label', `${name} value`);
        input.addEventListener('input', () => {
            state.current[name] = Number(input.value);
            readout.textContent = Number(input.value).toFixed(2);
            scheduleLivePrediction();
        });
        head.firstChild.htmlFor = input.id;

        wrap.append(head, input);
        box.appendChild(wrap);
    });
}

function resetWhatIf() {
    if (!state.original) return;
    state.current = { ...state.original };
    buildWhatIf();
    runPrediction({ log: false });
}

// ---------- prediction + result rendering ----------
function factorRow(f, maxAbs) {
    const row = el('div', 'factor-row');
    const track = el('div', 'factor-track');
    track.appendChild(el('div', 'mid'));
    const bar = el('div', `factor-bar ${f.direction === "fraud" ? "fraud" : "legit"}`);
    const half = (Math.abs(f.contribution) / maxAbs) * 50;
    bar.style.width = `${half}%`;
    bar.style.left = f.direction === "fraud" ? "50%" : `${50 - half}%`;
    track.appendChild(bar);
    row.append(el('span', 'fw-semibold', f.feature), track, el('span', 'text-end text-muted', f.value.toFixed(2)));
    row.title = `${f.feature} = ${f.value} pushes ${f.direction === "fraud" ? "toward fraud" : "toward legitimate"} (${f.contribution > 0 ? "+" : ""}${f.contribution})`;
    return row;
}

function renderResult(result) {
    $('result-empty').classList.add('d-none');
    $('prediction-result').classList.remove('d-none');

    const isFraud = result.prediction === "FRAUD";
    $('verdict').className = "verdict mb-3 " + (isFraud ? "fraud" : "legit");
    $('res-pred').textContent = result.prediction;
    $('res-level').textContent = result.risk_level;

    const prob = result.fraud_probability, thr = result.decision_threshold;
    $('res-prob').textContent = pct(prob);
    const fill = $('meter-fill');
    fill.style.width = `${Math.max(prob * 100, 1)}%`;
    fill.style.background = isFraud ? "#dc3545" : "#198754";
    $('meter-thresh').style.left = `${Math.min(thr * 100, 100)}%`;
    $('thresh-label').textContent = `alert at ${pct(thr, 0)}%`;

    // dataset label vs model verdict
    const note = $('match-note');
    note.className = "small mb-3";
    if (state.label && sameFeatures(state.current, state.original)) {
        const hit = state.label === result.prediction;
        note.textContent = hit
            ? `Dataset label is ${state.label}; the model agrees.`
            : `Dataset label is ${state.label}, but the model said ${result.prediction}. This is one of the cases it gets wrong.`;
        note.classList.add(hit ? "text-success" : "text-danger", "fw-semibold");
    } else if (state.label) {
        note.textContent = "You changed the values, so the dataset label no longer applies. This is a what-if result.";
        note.classList.add("text-muted");
    } else {
        note.textContent = "";
    }

    // factors
    const factors = result.top_factors || [];
    const maxAbs = Math.max(...factors.map(f => Math.abs(f.contribution)), 0.0001);
    $('factors').replaceChildren(...factors.map(f => factorRow(f, maxAbs)));

    if (factors.length) {
        const towardFraud = factors.filter(f => f.direction === "fraud")[0];
        const towardLegit = factors.filter(f => f.direction === "legitimate")[0];
        const parts = [`The model is ${pct(prob, 1)}% sure this is fraud, ${isFraud ? "above" : "below"} its ${pct(thr, 0)}% alert threshold.`];
        if (towardFraud) parts.push(`Strongest push toward fraud: ${towardFraud.feature} (${towardFraud.value}).`);
        if (towardLegit) parts.push(`Strongest push toward legitimate: ${towardLegit.feature} (${towardLegit.value}).`);
        parts.push("Features are anonymised components, so these show which pattern mattered, not a named reason.");
        $('summary-text').textContent = parts.join(" ");
    } else {
        $('summary-text').textContent = "";
    }

    $('res-model').textContent = result.model;
    $('res-feat-count').textContent = result.feature_count;
}

function sameFeatures(a, b) {
    return Object.keys(a).every(k => Number(a[k]) === Number(b[k]));
}

let requestSeq = 0;
async function runPrediction({ log }) {
    if (!state.current) return;
    clearError();
    const seq = ++requestSeq;
    const button = $('predict-btn');
    if (log) { button.disabled = true; button.textContent = "Analyzing..."; }
    try {
        const result = await apiJson(`${API_BASE}/predict/?log=${log}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ features: state.current })
        });
        if (seq !== requestSeq) return;   // a newer request superseded this one
        renderResult(result);
        if (log) refreshDashboard();
    } catch (e) {
        showError("Error making prediction: " + e.message);
    } finally {
        if (log) { button.disabled = false; button.innerHTML = "Analyze &amp; save to history"; }
    }
}

// ---------- wiring ----------
document.querySelectorAll('.scenario[data-type]').forEach(b => b.addEventListener('click', () => selectScenario(b)));
$('paste-toggle').addEventListener('click', togglePaste);
$('paste-load').addEventListener('click', loadPasted);
$('predict-btn').addEventListener('click', () => runPrediction({ log: true }));
$('reset-btn').addEventListener('click', resetWhatIf);
$('refresh-btn').addEventListener('click', refreshDashboard);
$('amount-input').addEventListener('input', (e) => {
    const v = Number(e.target.value);
    if (state.current && Number.isFinite(v) && v >= 0) {
        state.current.Amount = v;
        scheduleLivePrediction();
    }
});
$('honest-mode').addEventListener('change', () => {
    const active = document.querySelector('.scenario.active[data-type]');
    if (active) selectScenario(active);
});

loadModelCard();
refreshDashboard();
