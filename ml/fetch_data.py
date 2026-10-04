import os
import pandas as pd
from sklearn.datasets import fetch_openml
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_and_save_data(output_path):
    logging.info("Fetching Credit Card Fraud dataset from OpenML (ID 1597)...")
    try:
        # data_id=1597 is the credit card fraud dataset
        dataset = fetch_openml(data_id=1597, as_frame=True, parser='auto')
        df = dataset.frame
        
        logging.info(f"Dataset fetched successfully. Shape: {df.shape}")
        
        # Ensure 'Class' column is integer (0/1) instead of categorical string
        if 'Class' in df.columns:
             df['Class'] = df['Class'].astype(int)
        
        df.to_csv(output_path, index=False)
        logging.info(f"Dataset saved to {output_path}")
        
    except Exception as e:
        logging.error(f"Error fetching dataset: {e}")
        raise

if __name__ == "__main__":
    output_file = os.path.join(os.path.dirname(__file__), "..", "data", "creditcard.csv")
    fetch_and_save_data(output_file)
