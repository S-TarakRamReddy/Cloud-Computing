from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routes import prediction, transactions, statistics
from backend.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A Machine Learning and Cloud-Based Framework for Real-Time Transaction Fraud Risk Prediction",
    version="1.0.0"
)

import os

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8080")
origins = [frontend_url]
if frontend_url != "*":
    origins.append("http://127.0.0.1:8080")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if frontend_url != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prediction.router)
app.include_router(transactions.router)
app.include_router(statistics.router)
try:
    from backend.routes import demo
    app.include_router(demo.router)
except ImportError:
    pass

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy"}

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
import os

frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
