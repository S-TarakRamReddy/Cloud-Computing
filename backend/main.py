import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routes import prediction, transactions, statistics
from backend.config import settings
from backend.metrics import build_summary, metrics_middleware, render_metrics

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A Machine Learning and Cloud-Based Framework for Real-Time Transaction Fraud Risk Prediction",
    version="1.0.0"
)

app.middleware("http")(metrics_middleware)

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8080")
origins = [frontend_url]
if frontend_url != "*":
    origins.append("http://127.0.0.1:8080")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if frontend_url != "*" else ["*"],
    allow_credentials=frontend_url != "*",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prediction.router)
app.include_router(transactions.router)
app.include_router(statistics.router)
from backend.routes import demo
app.include_router(demo.router)

@app.get("/health", tags=["System"])
def health_check():
    from backend.services.ml_service import ml_service
    return {"status": "healthy" if ml_service.model else "degraded", "model_loaded": ml_service.model is not None}

@app.get("/metrics", tags=["System"], include_in_schema=False)
def metrics():
    """Prometheus scrape endpoint."""
    from backend.services.ml_service import ml_service
    return render_metrics(ml_service.model is not None)

@app.get("/monitoring/summary", tags=["System"])
def monitoring_summary():
    """Aggregates of recent traffic and predictions for the dashboard's Monitoring pane."""
    from backend.services.ml_service import ml_service
    return build_summary(ml_service.model_card, ml_service.model is not None)

@app.get("/model-card", tags=["System"])
def model_card():
    """Honest evaluation numbers, feature importance and typical feature ranges."""
    from backend.services.ml_service import ml_service
    if not ml_service.model_card:
        raise HTTPException(status_code=404, detail="Model card not available")
    return ml_service.model_card

@app.get("/model-info", tags=["System"])
def model_info():
    from backend.services.ml_service import ml_service
    if ml_service.model:
        return {
            "status": "loaded",
            "model_type": str(type(ml_service.model).__name__),
            "features_count": len(ml_service.feature_names) if ml_service.feature_names else 0
        }
    return {"status": "not_loaded"}

from fastapi.staticfiles import StaticFiles

frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
