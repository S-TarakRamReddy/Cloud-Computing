import os
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    PROJECT_NAME: str = "Cloud-Based Credit Card Fraud Detection System"
    DATABASE_URL: str = "sqlite:///./transactions.db" 
    
    MODEL_PATH: str = os.path.join(BASE_DIR, "ml", "model", "best_model.pkl")
    SCALER_PATH: str = os.path.join(BASE_DIR, "ml", "model", "scaler.pkl")
    FEATURE_NAMES_PATH: str = os.path.join(BASE_DIR, "ml", "model", "feature_names.pkl")

    class Config:
        env_file = ".env"

settings = Settings()
