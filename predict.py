from mongodb_client import predictions_collection
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import date, timedelta, datetime

#Can change these to test different stocks
DEFAULT_TICKER = "AAPL" 
DAYS_TO_PREDICT = 7     
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

def make_simple_prediction(df):
    #Linear Regression
    df['Day_Count'] = (df['Date'] - df['Date'].min()).dt.days
    X = df[['Day_Count']].values
    y = df['Close'].values 
    model = LinearRegression()
    model.fit(X, y)
    
    last_day_count = df['Day_Count'].iloc[-1]
    future_day_count = last_day_count + DAYS_TO_PREDICT
    predicted_price = model.predict(np.array([[future_day_count]]))[0].item()
    last_known_date = df['Date'].iloc[-1].date()
    target_date_raw = last_known_date + timedelta(days=DAYS_TO_PREDICT) 

    return {"prediction_date": datetime.combine(date.today(), datetime.min.time()), "target_date": datetime.combine(target_date_raw, datetime.min.time()), "predicted_price": round(predicted_price, 2)}


def generate_single_prediction(ticker):
    df = get_historical_data(ticker)
    if df is None:
        return None
        
    prediction_result = make_simple_prediction(df)
    prediction_result['ticker'] = ticker 
    prediction_result['model_version'] = "Simple-LinReg-90Day" 
    prediction_result['actual_price'] = None
    prediction_result['prediction_error_pct'] = None

    try:
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
