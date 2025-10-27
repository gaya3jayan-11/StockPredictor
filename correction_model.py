import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from mongodb_client import predictions_collection
import joblib # Library used to save and load Python objects (the model)

# Define file path to save the trained model
CORRECTION_MODEL_PATH = "correction_model.pkl"

def train_correction_model():
    """
    Trains a simple Linear Regression model to predict the ACTUAL price 
    using the PRIMARY model's PREDICTED price as the only feature.
    """
    print("\n--- Training Correction Model ---")
    
    # 1. Retrieve Audited Data from MongoDB (The Ground Truth)
    # Filter for documents where actual_price is NOT null (i.e., audited records)
    query = {"actual_price": {"$ne": None}}
    
    # Find all documents and convert the MongoDB cursor to a Python list
    data = list(predictions_collection.find(query))
    
    if not data or len(data) < 20: 
        print(f"ERROR: Not enough audited data ({len(data)} records found, need > 20) to train the correction model.")
        return None
        
    df = pd.DataFrame(data)
    
    # 2. Define Input (X) and Target (y)
    # X (Feature) is the primary model's PREDICTED price
    X = df['predicted_price'].values.reshape(-1, 1)
    
    # y (Target) is the ACTUAL price from the audit
    y = df['actual_price'].values
    
    # 3. Train the Correction Model (The "Tutor" learning the bias)
    correction_model = LinearRegression()
    correction_model.fit(X, y)
    
    # 4. Save the Model to Disk
    joblib.dump(correction_model, CORRECTION_MODEL_PATH)
    print(f"Correction Model trained and saved to {CORRECTION_MODEL_PATH}")
    return correction_model

def load_correction_model():
    """Loads the trained correction model from disk."""
    try:
        return joblib.load(CORRECTION_MODEL_PATH)
    except FileNotFoundError:
        return None

if __name__ == "__main__":
    # Test the training process
    train_correction_model()