import mongodb_client
from correction_model import load_correction_model, CORRECTION_MODEL_PATH 
import os 
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from sklearn.linear_model import LinearRegression
from datetime import date, timedelta, datetime

#Can change these to test different stocks
DEFAULT_TICKER = "AAPL"    
LOOKBACK_DAYS = 90     

def get_historical_data(ticker=DEFAULT_TICKER):
    today = date.today()
    #Get enough historical data
    start_date = today - timedelta(days=LOOKBACK_DAYS * 2) 
    
    try:
        #Scrape data from Yahoo Finance
        df = yf.download(ticker, start=start_date, end=today)
    except Exception as e:
        print(f"Error scraping data for {ticker}: {e}")
        return None

    if df.empty:
        print(f"No data found for {ticker}")
        return None
    
    df = df.tail(LOOKBACK_DAYS)
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date']) 
    
    return df

def make_simple_prediction(df, days_ahead):
    #Linear Regression
    df['Day_Count'] = (df['Date'] - df['Date'].min()).dt.days
    X = df[['Day_Count']].values
    y = df['Close'].values 
    model = LinearRegression()
    model.fit(X, y)
    
    last_day_count = df['Day_Count'].iloc[-1]
    future_day_count = last_day_count + days_ahead
    predicted_price = model.predict(np.array([[future_day_count]]))[0].item()
    last_known_date = df['Date'].iloc[-1].date()
    target_date_raw = last_known_date + timedelta(days=days_ahead)
    return {"prediction_date": datetime.combine(date.today(), datetime.min.time()), "target_date": datetime.combine(target_date_raw, datetime.min.time()), "predicted_price": round(predicted_price, 2)}


def generate_single_prediction(ticker, days_ahead):
    df = get_historical_data(ticker)
    if df is None:
        return None
        
    # --- 1. Primary Prediction (LinReg) ---
    linreg_prediction_result = make_simple_prediction(df, days_ahead)
    final_predicted_price = linreg_prediction_result['predicted_price']

    # --- 2. Model Correction (The Improvement) ---
    # Check if a corrected model exists to use
    model_name = f"LinReg-{days_ahead}Day"
    
    if os.path.exists(CORRECTION_MODEL_PATH):
        correction_model = load_correction_model()
        if correction_model:
            # Apply the correction: Primary prediction is input to the correction model
            input_price = np.array([[final_predicted_price]])
            corrected_price = correction_model.predict(input_price)[0].item()
            
            # Use the corrected price as the final output
            final_predicted_price = round(corrected_price, 2)
            model_name = f"LinReg-{days_ahead}Day-Corrected" # Track the corrected version
            print(f"Correction applied. Final Price: ${final_predicted_price:.2f}")

    # --- 3. Final BDA Document Setup ---
    prediction_result = linreg_prediction_result 
    
    # Update the core prediction metrics with the FINAL, CORRECTED value
    prediction_result['predicted_price'] = final_predicted_price 
    prediction_result['ticker'] = ticker 
    prediction_result['model_version'] = model_name # Save the variable model version
    prediction_result['actual_price'] = None
    prediction_result['prediction_error_pct'] = None

    # --- 4. MongoDB Insertion ---
    predictions_collection = mongodb_client.predictions_collection
    if predictions_collection is None:
        print("FATAL DB ERROR: MongoDB collection not available.")
        return None

    try:
        # Insert the final, corrected prediction into MongoDB
        result = predictions_collection.insert_one(
            {
                "ticker": prediction_result['ticker'],
                "prediction_date": prediction_result['prediction_date'],
                "target_date": prediction_result['target_date'],
                "predicted_price": prediction_result['predicted_price'],
                "model_version": prediction_result['model_version'],
                "actual_price": prediction_result['actual_price'],
                "prediction_error_pct": prediction_result['prediction_error_pct']
            }
        )
        print(f"MongoDB: Successfully inserted prediction for {ticker}. ID: {result.inserted_id}")
    except Exception as e:
        print(f"MongoDB ERROR: Failed to insert prediction for {ticker}: {e}")
    
    return prediction_result
