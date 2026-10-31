import joblib
import numpy as np
from backend.config import settings
import logging

logging.basicConfig(level=logging.INFO)

import os
import json

class FeatureValidationError(ValueError):
    def __init__(self, missing, extra, message=None):
        self.missing, self.extra = missing, extra
        super().__init__(message or f"Invalid features. Missing: {missing}. Unexpected: {extra}.")


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

        missing = [fn for fn in self.feature_names if fn not in features_dict]
        extra = [k for k in features_dict if k not in self.feature_names]
        if missing or extra:
            raise FeatureValidationError(missing, extra)

        feature_values = [features_dict[fn] for fn in self.feature_names]
        if not np.all(np.isfinite(feature_values)):
            raise FeatureValidationError([], [], "Feature values must be finite numbers.")

        features_array = np.array(feature_values).reshape(1, -1)
        scaled_features = self.scaler.transform(features_array)
        
        prob = self.model.predict_proba(scaled_features)[0][1]
        
        # Use optimized threshold
        is_fraud = prob >= self.threshold
        
        # LOW below the threshold, MEDIUM up to 1.5x, HIGH above (matches report Ch. 6.6)
        risk_level = "LOW"
        if prob > self.threshold * 1.5:
            risk_level = "HIGH"
        elif is_fraud:
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
