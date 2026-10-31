import joblib
import numpy as np
import xgboost as xgb
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
        self.model_card = {}
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
            card_path = os.path.join(os.path.dirname(settings.MODEL_PATH), "model_card.json")
            if os.path.exists(card_path):
                with open(card_path, 'r') as f:
                    self.model_card = json.load(f)
            logging.info(f"ML artifacts loaded successfully. Decision Threshold: {self.threshold}")
        except Exception as e:
            logging.error(f"Error loading ML artifacts: {e}")
            self._log_environment()
            self.model = None

    @staticmethod
    def _log_environment():
        """Log what the container actually holds, to diagnose missing model files in deployment."""
        model_dir = os.path.dirname(settings.MODEL_PATH)
        logging.error(f"cwd={os.getcwd()} PORT={os.getenv('PORT')} PYTHONPATH={os.getenv('PYTHONPATH')}")
        for path in (os.path.dirname(model_dir), model_dir):
            try:
                logging.error(f"Contents of {path}: {sorted(os.listdir(path))}")
            except OSError as err:
                logging.error(f"Cannot list {path}: {err}")

    def explain(self, features_dict: dict, top_n: int = 6):
        """Per-feature contributions (log-odds) from the underlying XGBoost booster.

        Positive values push the score toward FRAUD, negative toward LEGITIMATE. The isotonic
        calibration is monotonic, so the direction of each push carries over to the final probability.
        """
        try:
            values = np.array([features_dict[fn] for fn in self.feature_names], dtype=float).reshape(1, -1)
            scaled = self.scaler.transform(values)
            booster = self.model.calibrated_classifiers_[0].estimator.get_booster()
            contribs = booster.predict(xgb.DMatrix(scaled), pred_contribs=True)[0][:-1]
        except Exception:
            logging.exception("Could not compute explanation")
            return []
        order = np.argsort(np.abs(contribs))[::-1][:top_n]
        return [
            {
                "feature": self.feature_names[i],
                "value": round(float(features_dict[self.feature_names[i]]), 4),
                "contribution": round(float(contribs[i]), 4),
                "direction": "fraud" if contribs[i] > 0 else "legitimate",
            }
            for i in order
        ]

    def sensitivity(self, features_dict: dict, feature: str, low: float, high: float, points: int = 60):
        """Fraud probability as one feature sweeps from low to high, all others held fixed."""
        if feature not in self.feature_names:
            raise FeatureValidationError([], [feature], f"Unknown feature: {feature}")
        base = np.array([features_dict[fn] for fn in self.feature_names], dtype=float)
        values = np.linspace(low, high, points)
        batch = np.tile(base, (points, 1))
        batch[:, self.feature_names.index(feature)] = values
        probs = self.model.predict_proba(self.scaler.transform(batch))[:, 1]
        return [round(float(v), 4) for v in values], [round(float(p), 4) for p in probs]

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
            "feature_count": len(self.feature_names),
            "top_factors": self.explain(features_dict),
        }

ml_service = MLService()
