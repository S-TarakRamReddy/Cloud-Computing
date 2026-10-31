import os
import logging
from ml.fetch_data import fetch_and_save_data
from ml.preprocess import preprocess_data
from ml.train import main as train_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run():
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "..", "data", "creditcard.csv")
    model_dir = os.path.join(base_dir, "model")
    
    # 1. Fetch
    if not os.path.exists(data_path):
        fetch_and_save_data(data_path)
    else:
        logging.info("Dataset already exists. Skipping fetch.")
        
    # 2. Preprocess
    preprocess_data(data_path, model_dir)
    
    # 3. Train
    train_model()

if __name__ == "__main__":
    run()
