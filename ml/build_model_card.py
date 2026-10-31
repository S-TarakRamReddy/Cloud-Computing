"""Build ml/model/model_card.json: honest metrics (with bootstrap CIs), confusion matrix,
global feature importance and typical feature ranges, used by the dashboard.

Usage (needs ml/model/preprocessed_data.pkl from `python -m ml.preprocess`):
    python -m ml.build_model_card
"""
import json
import os
import platform

import joblib
import numpy as np
import sklearn
import xgboost as xgb
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

BASE = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE, "model")
N_BOOT = 1000
SEED = 42


def ci(values):
    lo, hi = np.percentile(values, [2.5, 97.5])
    return [round(float(lo), 4), round(float(hi), 4)]


def main():
    data = joblib.load(os.path.join(MODEL_DIR, "preprocessed_data.pkl"))
    model = joblib.load(os.path.join(MODEL_DIR, "best_model.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    names = joblib.load(os.path.join(MODEL_DIR, "feature_names.pkl"))
    threshold = json.load(open(os.path.join(MODEL_DIR, "threshold.json")))["threshold"]

    X_test, y_test = np.asarray(data["X_test"]), np.asarray(data["y_test"])
    prob = model.predict_proba(X_test)[:, 1]
    pred = (prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()

    rng = np.random.default_rng(SEED)
    boot = {"precision": [], "recall": [], "f1": [], "pr_auc": []}
    n = len(y_test)
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, n)
        yt, pb, pd_ = y_test[idx], prob[idx], pred[idx]
        if yt.sum() == 0:
            continue
        boot["precision"].append(precision_score(yt, pd_, zero_division=0))
        boot["recall"].append(recall_score(yt, pd_))
        boot["f1"].append(f1_score(yt, pd_, zero_division=0))
        boot["pr_auc"].append(average_precision_score(yt, pb))

    # Global importance: mean |contribution| (log-odds) of the underlying booster on the test set
    booster = model.calibrated_classifiers_[0].estimator.get_booster()
    contribs = booster.predict(xgb.DMatrix(X_test), pred_contribs=True)[:, :-1]
    importance = np.abs(contribs).mean(axis=0)
    importance = importance / importance.sum()

    # Typical raw ranges (1st-99th percentile) for what-if sliders
    raw = scaler.inverse_transform(X_test)
    ranges = {nm: [round(float(np.percentile(raw[:, i], 1)), 3), round(float(np.percentile(raw[:, i], 99)), 3)]
              for i, nm in enumerate(names)}

    # How trustworthy each score band is: what share of test transactions in the band were fraud
    bands = [(0.0, 0.01), (0.01, 0.05), (0.05, 0.21), (0.21, 0.5), (0.5, 0.95), (0.95, 1.0001)]
    reliability = []
    for lo, hi in bands:
        sel = (prob >= lo) & (prob < hi)
        reliability.append({"low": lo, "high": min(hi, 1.0), "transactions": int(sel.sum()),
                            "fraud": int(y_test[sel].sum())})

    # Real borderline transactions (model unsure) for the demo; mixes both true labels
    mid = np.where((prob > 0.15) & (prob < 0.95))[0]
    rng_pick = np.random.default_rng(SEED)
    picks = []
    for label in (1, 0):
        pool = [i for i in mid if y_test[i] == label]
        rng_pick.shuffle(pool)
        picks += pool[:8]
    borderline = [{"label": "FRAUD" if y_test[i] else "LEGITIMATE",
                   "features": {nm: round(float(raw[i, j]), 6) for j, nm in enumerate(names)}} for i in picks]
    demo_path = os.path.join(BASE, "..", "backend", "demo_data.json")
    with open(demo_path) as f:
        demo = json.load(f)
    demo["borderline"] = borderline
    with open(demo_path, "w") as f:
        json.dump(demo, f)

    card = {
        "threshold": round(float(threshold), 4),
        "test_set": {"rows": int(n), "fraud_cases": int(y_test.sum())},
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "metrics": {
            "precision": {"value": round(float(precision_score(y_test, pred)), 4), "ci95": ci(boot["precision"])},
            "recall": {"value": round(float(recall_score(y_test, pred)), 4), "ci95": ci(boot["recall"])},
            "f1": {"value": round(float(f1_score(y_test, pred)), 4), "ci95": ci(boot["f1"])},
            "pr_auc": {"value": round(float(average_precision_score(y_test, prob)), 4), "ci95": ci(boot["pr_auc"])},
            "roc_auc": {"value": round(float(roc_auc_score(y_test, prob)), 4)},
        },
        "bootstrap": {"resamples": N_BOOT, "seed": SEED},
        "reliability": reliability,
        "feature_importance": {nm: round(float(v), 4) for nm, v in zip(names, importance)},
        "feature_ranges": ranges,
        "versions": {"python": platform.python_version(), "scikit_learn": sklearn.__version__, "xgboost": xgb.__version__},
    }
    out = os.path.join(MODEL_DIR, "model_card.json")
    with open(out, "w") as f:
        json.dump(card, f, indent=2)
    print("wrote", out)
    print(json.dumps({k: card[k] for k in ("confusion_matrix", "metrics", "test_set")}, indent=2))


if __name__ == "__main__":
    main()
