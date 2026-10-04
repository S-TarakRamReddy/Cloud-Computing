import joblib
import numpy as np
import pandas as pd
from backend.config import settings
import logging

logging.basicConfig(level=logging.INFO)

import os
import json

class MLService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.threshold = 0.5
        self.load_artifacts()

    def load_artifacts(self):
        try:
            logging.info(f"Loading ML artifacts from {settings.MODEL_PATH}")
            self.model = joblib.load(settings.MODEL_PATH)
            self.scaler = joblib.load(settings.SCALER_PATH)
            self.feature_names = joblib.load(settings.FEATURE_NAMES_PATH)
            
            # Load threshold
            thresh_path = os.path.join(os.path.dirname(settings.MODEL_PATH), "threshold.json")
            if os.path.exists(thresh_path):
                with open(thresh_path, 'r') as f:
                    data = json.load(f)
                    self.threshold = data.get("threshold", 0.5)
            logging.info(f"ML artifacts loaded successfully. Decision Threshold: {self.threshold}")
        except Exception as e:
            logging.error(f"Error loading ML artifacts: {e}")
            self.model = None

    def predict(self, features_dict: dict):
        if not self.model or not self.scaler:
            raise ValueError("ML model is not loaded.")

        feature_values = []
        for fn in self.feature_names:
            feature_values.append(features_dict.get(fn, 0.0))
            
        features_array = np.array(feature_values).reshape(1, -1)
        scaled_features = self.scaler.transform(features_array)
        
        prob = self.model.predict_proba(scaled_features)[0][1]
        
        # Use optimized threshold
        is_fraud = prob >= self.threshold
        
        risk_level = "LOW"
        if prob > self.threshold * 1.5:
            risk_level = "HIGH"
        elif prob > self.threshold * 0.8:
            risk_level = "MEDIUM"
            
        return {
            "prediction": "FRAUD" if is_fraud else "LEGITIMATE",
            "fraud_probability": round(float(prob), 6),
            "risk_level": risk_level,
            "decision_threshold": round(float(self.threshold), 6),
            "model": type(self.model).__name__,
            "feature_count": len(self.feature_names)
        }

ml_service = MLService()
