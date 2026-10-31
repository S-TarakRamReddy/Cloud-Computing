"""Monitoring for the API.

Two views of the same traffic:
  * Prometheus metrics at /metrics (for Prometheus and Grafana)
  * a bounded in-memory event log behind /monitoring/summary (for the built-in dashboard pane)

The event log needs no extra services. It lives in this process, so it resets on restart and,
with several worker processes, each worker has its own log.
"""
import math
import threading
import time
from collections import deque
from datetime import datetime, timezone

from fastapi import Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

REQUESTS = Counter("fraud_api_requests_total", "HTTP requests handled", ["method", "path", "status"])
LATENCY = Histogram(
    "fraud_api_request_seconds", "HTTP request latency in seconds", ["path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
PREDICTIONS = Counter("fraud_predictions_total", "Predictions made, by verdict and risk level", ["prediction", "risk_level"])
SCORES = Histogram(
    "fraud_prediction_probability", "Distribution of predicted fraud probabilities",
    buckets=(0.01, 0.05, 0.1, 0.21, 0.315, 0.5, 0.8, 0.95, 0.99, 1.0),
)
MODEL_LOADED = Gauge("fraud_model_loaded", "1 if the ML model loaded successfully, else 0")

# ---------- in-memory event log for the dashboard pane ----------
MAX_EVENTS = 5000
EVENTS: deque = deque(maxlen=MAX_EVENTS)
_LOCK = threading.Lock()
STARTED_AT = time.time()
TOTALS = {"requests": 0, "predictions": 0, "flagged": 0, "errors": 0}
HIDDEN_PATHS = {"/metrics", "/monitoring/summary", "static"}  # not counted as API traffic in the pane


def _path_label(request: Request) -> str:
    """Route template (e.g. /transactions/{tx_id}) so label cardinality stays bounded."""
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    if path:
        return path
    return "static" if request.url.path != "/metrics" else "/metrics"


async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        path = _path_label(request)
        elapsed = time.perf_counter() - start
        if path != "/metrics":
            LATENCY.labels(path=path).observe(elapsed)
            REQUESTS.labels(method=request.method, path=path, status=str(status)).inc()
        if path not in HIDDEN_PATHS:
            with _LOCK:
                TOTALS["requests"] += 1
                if status >= 400:
                    TOTALS["errors"] += 1
                EVENTS.append({"t": time.time(), "kind": "request", "path": path, "method": request.method,
                               "status": status, "ms": elapsed * 1000})


def record_prediction(result: dict) -> None:
    PREDICTIONS.labels(prediction=result["prediction"], risk_level=result["risk_level"]).inc()
    SCORES.observe(result["fraud_probability"])
    with _LOCK:
        TOTALS["predictions"] += 1
        if result["prediction"] == "FRAUD":
            TOTALS["flagged"] += 1
        EVENTS.append({"t": time.time(), "kind": "prediction", "p": result["fraud_probability"],
                       "verdict": result["prediction"], "risk": result["risk_level"]})


def render_metrics(model_loaded: bool) -> Response:
    MODEL_LOADED.set(1 if model_loaded else 0)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ---------- summary for the dashboard pane ----------
def _percentile(sorted_values, q):
    if not sorted_values:
        return None
    rank = max(1, math.ceil(q * len(sorted_values)))
    return round(sorted_values[rank - 1], 2)


def build_summary(model_card: dict, model_loaded: bool, window_minutes: int = 30) -> dict:
    now = time.time()
    with _LOCK:
        events = list(EVENTS)
        totals = dict(TOTALS)
    start_minute = int(now // 60) * 60 - (window_minutes - 1) * 60

    minutes = [{"t": start_minute + i * 60, "requests": 0, "predictions": 0, "errors": 0} for i in range(window_minutes)]
    latencies, recent = [], []
    verdicts, risks = {"FRAUD": 0, "LEGITIMATE": 0}, {"LOW": 0, "MEDIUM": 0, "HIGH": 0}

    bands = (model_card or {}).get("reliability") or [
        {"low": 0.0, "high": 0.01}, {"low": 0.01, "high": 0.05}, {"low": 0.05, "high": 0.21},
        {"low": 0.21, "high": 0.5}, {"low": 0.5, "high": 0.95}, {"low": 0.95, "high": 1.0}]
    live_counts = [0] * len(bands)
    window_predictions = 0

    for e in events:
        if e["t"] < start_minute:
            continue
        idx = int((e["t"] - start_minute) // 60)
        if not 0 <= idx < window_minutes:
            continue
        if e["kind"] == "request":
            minutes[idx]["requests"] += 1
            if e["status"] >= 400:
                minutes[idx]["errors"] += 1
            if e["path"] == "/predict/" and e["method"] == "POST" and e["status"] == 200:
                latencies.append(e["ms"])
        else:
            minutes[idx]["predictions"] += 1
            window_predictions += 1
            verdicts[e["verdict"]] = verdicts.get(e["verdict"], 0) + 1
            risks[e["risk"]] = risks.get(e["risk"], 0) + 1
            for b, band in enumerate(bands):
                if band["low"] <= e["p"] < band["high"] or (band["high"] >= 1.0 and e["p"] >= band["low"]):
                    live_counts[b] += 1
                    break
            recent.append({"time": datetime.fromtimestamp(e["t"], tz=timezone.utc).isoformat(), "verdict": e["verdict"],
                           "probability": round(e["p"], 4), "risk": e["risk"]})

    latencies.sort()
    has_baseline = "transactions" in bands[0]
    baseline_total = sum(b["transactions"] for b in bands) if has_baseline else 0
    baseline_share = [round(b["transactions"] / baseline_total, 6) for b in bands] if baseline_total else None
    cm = (model_card or {}).get("confusion_matrix") or {}
    rows = ((model_card or {}).get("test_set") or {}).get("rows")
    baseline_flag_rate = round((cm.get("tp", 0) + cm.get("fp", 0)) / rows, 6) if cm and rows else None

    return {
        "generated_at": datetime.fromtimestamp(now, tz=timezone.utc).isoformat(),
        "window_minutes": window_minutes,
        "uptime_seconds": int(now - STARTED_AT),
        "model_loaded": model_loaded,
        "totals_since_start": totals,
        "timeline": minutes,
        "latency_ms": {"count": len(latencies), "p50": _percentile(latencies, 0.50),
                       "p95": _percentile(latencies, 0.95), "max": round(latencies[-1], 2) if latencies else None},
        "predictions": {"in_window": window_predictions, "verdicts": verdicts, "risk_levels": risks,
                        "flag_rate": round(verdicts.get("FRAUD", 0) / window_predictions, 4) if window_predictions else None,
                        "baseline_flag_rate": baseline_flag_rate},
        "score_distribution": {
            "bands": [{"low": b["low"], "high": b["high"]} for b in bands],
            "live_counts": live_counts,
            "baseline_share": baseline_share,
        },
        "recent_predictions": list(reversed(recent))[:10],
    }
