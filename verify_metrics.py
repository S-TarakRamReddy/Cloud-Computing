import os
import joblib
import json
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, brier_score_loss

base_dir = os.path.dirname(__file__)
model_dir = os.path.join(base_dir, 'ml', 'model')

model = joblib.load(os.path.join(model_dir, 'best_model.pkl'))
data = joblib.load(os.path.join(model_dir, 'preprocessed_data.pkl'))
thresh = json.load(open(os.path.join(model_dir, 'threshold.json')))['threshold']

X_test, y_test = data['X_test'], data['y_test']
y_prob = model.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= thresh).astype(int)

# 1. Recalculate metrics
print("--- Final Metrics Recalculation ---")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.6f}")
print(f"Precision: {precision_score(y_test, y_pred, zero_division=0):.6f}")
print(f"Recall: {recall_score(y_test, y_pred, zero_division=0):.6f}")
print(f"F1: {f1_score(y_test, y_pred, zero_division=0):.6f}")
print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.6f}")
print(f"PR-AUC: {average_precision_score(y_test, y_prob):.6f}")
print(f"Brier Score: {brier_score_loss(y_test, y_prob):.6f}")

# 2. Find Low, Medium, High examples
high_idx = np.where(y_prob > thresh * 1.5)[0]
med_idx = np.where((y_prob > thresh * 0.8) & (y_prob <= thresh * 1.5))[0]
low_idx = np.where(y_prob <= thresh * 0.8)[0]

def print_example(name, idx_list):
    if len(idx_list) > 0:
        idx = idx_list[0]
        prob = y_prob[idx]
        actual = y_test.iloc[idx]
        pred = y_pred[idx]
        print(f"\n{name} Risk Example:")
        print(f"Actual label: {'FRAUD' if actual==1 else 'LEGITIMATE'}")
        print(f"Predicted label: {'FRAUD' if pred==1 else 'LEGITIMATE'}")
        print(f"Calibrated probability: {prob * 100:.4f}%")
        print(f"Threshold: {thresh * 100:.4f}%")

print_example("LOW", low_idx)
print_example("MEDIUM", med_idx)
print_example("HIGH", high_idx)
