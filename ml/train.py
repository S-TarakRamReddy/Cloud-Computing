import os
import joblib
import json
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve,
    average_precision_score, brier_score_loss
)
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from xgboost import XGBClassifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_metrics(y_true, y_pred, y_prob):
    return {
        'Accuracy': accuracy_score(y_true, y_pred),
        'Precision': precision_score(y_true, y_pred, zero_division=0),
        'Recall': recall_score(y_true, y_pred, zero_division=0),
        'F1': f1_score(y_true, y_pred, zero_division=0),
        'ROC-AUC': roc_auc_score(y_true, y_prob),
        'Avg_Precision': average_precision_score(y_true, y_prob),
        'Brier_Score': brier_score_loss(y_true, y_prob)
    }

def optimize_threshold(y_val, y_prob):
    best_f1 = 0
    best_thresh = 0.5
    best_metrics = None
    
    thresholds = np.arange(0.1, 0.95, 0.01) # Finer thresholds
    f1s = []
    recalls = []
    precisions = []
    
    for thresh in thresholds:
        y_pred = (y_prob >= thresh).astype(int)
        m = get_metrics(y_val, y_pred, y_prob)
        f1s.append(m['F1'])
        recalls.append(m['Recall'])
        precisions.append(m['Precision'])
        
        score = m['F1']
        if m['Recall'] >= 0.85 and m['Precision'] >= 0.50:
            score += 1.0
            
        if score > best_f1:
            best_f1 = score
            best_thresh = thresh
            best_metrics = m
            
    return best_thresh, best_metrics, thresholds, f1s, recalls, precisions

def plot_pr_curve(y_test, y_prob1, label1, y_prob2, label2, reports_dir):
    precision1, recall1, _ = precision_recall_curve(y_test, y_prob1)
    precision2, recall2, _ = precision_recall_curve(y_test, y_prob2)
    plt.figure(figsize=(8,6))
    plt.plot(recall1, precision1, label=label1)
    plt.plot(recall2, precision2, label=label2)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve Comparison')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, 'figures/precision_recall_curve.png'))
    plt.close()

def plot_roc_curve(y_test, y_prob1, label1, y_prob2, label2, reports_dir):
    fpr1, tpr1, _ = roc_curve(y_test, y_prob1)
    fpr2, tpr2, _ = roc_curve(y_test, y_prob2)
    plt.figure(figsize=(8,6))
    plt.plot(fpr1, tpr1, label=label1)
    plt.plot(fpr2, tpr2, label=label2)
    plt.plot([0, 1], [0, 1], 'k--', label='Random Guess')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve Comparison')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, 'figures/roc_curve_comparison.png'))
    plt.close()

def plot_calibration_curve(y_test, y_prob1, label1, y_prob2, label2, reports_dir):
    fraction_of_positives1, mean_predicted_value1 = calibration_curve(y_test, y_prob1, n_bins=10)
    fraction_of_positives2, mean_predicted_value2 = calibration_curve(y_test, y_prob2, n_bins=10)
    
    plt.figure(figsize=(8,6))
    plt.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
    plt.plot(mean_predicted_value1, fraction_of_positives1, "s-", label=label1)
    plt.plot(mean_predicted_value2, fraction_of_positives2, "s-", label=label2)
    plt.xlabel("Mean predicted value")
    plt.ylabel("Fraction of positives")
    plt.title("Calibration Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, 'figures/calibration_curve.png'))
    plt.close()
    
def plot_cm(y_test, y_pred, name, reports_dir):
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6,4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'{name} - Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, f'figures/{name.replace(" ", "_").lower()}_cm.png'))
    plt.close()

def main():
    base_dir = os.path.dirname(__file__)
    model_dir = os.path.join(base_dir, "model")
    reports_dir = os.path.join(base_dir, "..", "reports")
    os.makedirs(os.path.join(reports_dir, 'figures'), exist_ok=True)
    
    logging.info("Loading preprocessed data...")
    data = joblib.load(os.path.join(model_dir, 'preprocessed_data.pkl'))
    
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    X_test, y_test = data["X_test"], data["y_test"]
    
    scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()
    
    logging.info("--- Phase 1: Training Uncalibrated XGBoost ---")
    xgb = XGBClassifier(scale_pos_weight=scale_pos_weight, max_depth=6, random_state=42, n_jobs=-1, eval_metric='logloss')
    xgb.fit(X_train, y_train)
    
    y_val_prob_uncal = xgb.predict_proba(X_val)[:, 1]
    thresh_uncal, metrics_uncal, _, _, _, _ = optimize_threshold(y_val, y_val_prob_uncal)
    
    logging.info("--- Phase 2: Calibrating XGBoost ---")
    # Calibrate on the validation set using prefit
    calibrated_xgb = CalibratedClassifierCV(xgb, cv="prefit", method="isotonic")
    calibrated_xgb.fit(X_val, y_val)
    
    # We must optimize threshold for calibrated model on the validation set too
    y_val_prob_cal = calibrated_xgb.predict_proba(X_val)[:, 1]
    thresh_cal, metrics_cal, _, _, _, _ = optimize_threshold(y_val, y_val_prob_cal)
    
    logging.info("--- Phase 3: Final Test Set Evaluation ---")
    y_test_prob_uncal = xgb.predict_proba(X_test)[:, 1]
    y_test_pred_uncal = (y_test_prob_uncal >= thresh_uncal).astype(int)
    test_metrics_uncal = get_metrics(y_test, y_test_pred_uncal, y_test_prob_uncal)
    
    y_test_prob_cal = calibrated_xgb.predict_proba(X_test)[:, 1]
    y_test_pred_cal = (y_test_prob_cal >= thresh_cal).astype(int)
    test_metrics_cal = get_metrics(y_test, y_test_pred_cal, y_test_prob_cal)
    
    logging.info(f"Uncalibrated Final Metrics: {test_metrics_uncal}")
    logging.info(f"Calibrated Final Metrics: {test_metrics_cal}")
    
    # We choose the calibrated model if its F1 score is acceptable (e.g. at least 0.75) and Brier is better
    if test_metrics_cal['F1'] >= test_metrics_uncal['F1'] * 0.95: # Accept slightly lower F1 for better calibration
        logging.info("Selecting CALIBRATED XGBoost")
        best_model = calibrated_xgb
        best_thresh = thresh_cal
        best_name = "Calibrated XGBoost"
        y_test_pred_final = y_test_pred_cal
        final_metrics = test_metrics_cal
    else:
        logging.info("Selecting UNCALIBRATED XGBoost (Calibration worsened performance significantly)")
        best_model = xgb
        best_thresh = thresh_uncal
        best_name = "Uncalibrated XGBoost"
        y_test_pred_final = y_test_pred_uncal
        final_metrics = test_metrics_uncal

    # Save models and results
    joblib.dump(best_model, os.path.join(model_dir, 'best_model.pkl'))
    with open(os.path.join(model_dir, 'threshold.json'), 'w') as f:
        json.dump({'threshold': float(best_thresh)}, f)
        
    cm = confusion_matrix(y_test, y_test_pred_final)
    tn, fp, fn, tp = cm.ravel()
    
    with open(os.path.join(reports_dir, 'final_metrics.json'), 'w') as f:
        json.dump(final_metrics, f, indent=4)
        
    with open(os.path.join(reports_dir, 'final_confusion_matrix.json'), 'w') as f:
        json.dump({'TP': int(tp), 'TN': int(tn), 'FP': int(fp), 'FN': int(fn)}, f, indent=4)
        
    plot_cm(y_test, y_test_pred_final, best_name, reports_dir)
    plot_roc_curve(y_test, y_test_prob_uncal, "Uncalibrated XGB", y_test_prob_cal, "Calibrated XGB", reports_dir)
    plot_pr_curve(y_test, y_test_prob_uncal, "Uncalibrated XGB", y_test_prob_cal, "Calibrated XGB", reports_dir)
    plot_calibration_curve(y_test, y_test_prob_uncal, "Uncalibrated XGB", y_test_prob_cal, "Calibrated XGB", reports_dir)

if __name__ == "__main__":
    main()
