"""Prometheus metrics for the API: request counts, latency, predictions by verdict, model state."""
import time

from fastapi import Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

REQUESTS = Counter("fraud_api_requests_total", "HTTP requests handled", ["method", "path", "status"])
LATENCY = Histogram(
    "fraud_api_request_seconds", "HTTP request latency in seconds", ["path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
PREDICTIONS = Counter("fraud_predictions_total", "Predictions made, by verdict and risk level", ["prediction", "risk_level"])
MODEL_LOADED = Gauge("fraud_model_loaded", "1 if the ML model loaded successfully, else 0")


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
        if path != "/metrics":
            LATENCY.labels(path=path).observe(time.perf_counter() - start)
            REQUESTS.labels(method=request.method, path=path, status=str(status)).inc()


def record_prediction(result: dict) -> None:
    PREDICTIONS.labels(prediction=result["prediction"], risk_level=result["risk_level"]).inc()


def render_metrics(model_loaded: bool) -> Response:
    MODEL_LOADED.set(1 if model_loaded else 0)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
