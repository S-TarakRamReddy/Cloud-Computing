import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import joblib
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def preprocess_data(data_path, output_dir, random_state=42):
    logging.info(f"Loading data from {data_path}")
    df = pd.read_csv(data_path)
    
    # Remove duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        logging.info(f"Removing {duplicates} duplicate rows.")
        df = df.drop_duplicates()
        
    X = df.drop('Class', axis=1)
    y = df['Class']
    
    logging.info(f"Data shape after deduplication: {df.shape}")
    logging.info(f"Class distribution:\n{y.value_counts(normalize=True)}")
    
    # Train-val-test split (70-15-15)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, random_state=random_state, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.1765, random_state=random_state, stratify=y_train_val
    ) # 0.1765 of 0.85 is roughly 0.15
    
    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # SMOTE to handle class imbalance (Apply ONLY on training data)
    logging.info("Applying SMOTE to training data...")
    smote = SMOTE(random_state=random_state)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)
    
    logging.info(f"Resampled training shape: X={X_train_resampled.shape}, y={y_train_resampled.shape}")
    logging.info(f"Validation shape: X={X_val_scaled.shape}, y={y_val.shape}")
    logging.info(f"Test shape: X={X_test_scaled.shape}, y={y_test.shape}")
    
    # Save artifacts
    os.makedirs(output_dir, exist_ok=True)
    
    joblib.dump(scaler, os.path.join(output_dir, 'scaler.pkl'))
    joblib.dump({
        "X_train": X_train_scaled, "y_train": y_train,
        "X_train_smote": X_train_resampled, "y_train_smote": y_train_resampled,
        "X_val": X_val_scaled, "y_val": y_val,
        "X_test": X_test_scaled, "y_test": y_test
    }, os.path.join(output_dir, 'preprocessed_data.pkl'))
    
    # Also save column names for later reference in API
    joblib.dump(list(X.columns), os.path.join(output_dir, 'feature_names.pkl'))
    
    logging.info(f"Preprocessing artifacts saved to {output_dir}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "..", "data", "creditcard.csv")
    output_dir = os.path.join(base_dir, "model")
    preprocess_data(data_path, output_dir)
