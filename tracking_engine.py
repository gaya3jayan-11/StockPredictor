import yfinance as yf
from datetime import date, timedelta, datetime
from mongodb_client import predictions_collection
import pandas as pd

def update_actual_prices():
    """
    Finds past predictions with missing actual prices, fetches the actual price, 
    calculates accuracy, and updates the MongoDB document.
    """
    today = datetime.combine(date.today(), datetime.min.time())
    
    # 1. MongoDB Query: Find all predictions whose target_date is in the past AND 
    #    the actual_price field is currently missing (None).
    query = {
        "target_date": {"$lt": today}, # Target date is less than today (in the past)
        "actual_price": None          # The actual price has not yet been recorded
    }
    
    count = predictions_collection.count_documents(query)

    if count == 0:
        print("Tracking: No past predictions found that need updating.")
        return
        
    print(f"Tracking: Found {count} predictions to update...")
    
    # 2. Get the actual documents to iterate over (use the find() call here)
    predictions_to_update = predictions_collection.find(query)
    
    # Use a dictionary to store fetched prices to avoid duplicate yfinance calls
    fetched_prices = {}

    for pred in predictions_to_update:
        ticker = pred['ticker']
        target_date_dt = pred['target_date'] 
        
        target_date_str = target_date_dt.strftime('%Y-%m-%d')
        
        # Calculate the end date as the day AFTER the target date (yfinance uses exclusive end dates)
        end_date_str = (target_date_dt + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 2. Fetch Actual Price (using yfinance)
        if (ticker, target_date_str) not in fetched_prices:
            # Fetch data for the specific day
            # 💡 FIX 2: Pass both dates as clean strings
            data = yf.download(ticker, start=target_date_str, end=end_date_str)
            
            if not data.empty:
                # 💡 FIX 1: Use .item() to extract the pure Python float value
                actual_price = data['Close'].iloc[0].item() 
                
                # We round it later, but store the clean float value now
                fetched_prices[(ticker, target_date_str)] = actual_price
            else:
                # If no trade on that day, skip this prediction
                print(f"Tracking: No actual price found for {ticker} on {target_date_str}. Skipping.")
                continue

        actual_price_raw = fetched_prices[(ticker, target_date_str)]
        predicted_price = pred['predicted_price']

        # 3. Calculate Accuracy (BDA Metric)
        error_pct_raw = abs(predicted_price - actual_price_raw) / actual_price_raw * 100
        
        # 4. MongoDB Update: Use the $set operator to add the results
        update_operation = {
            "$set": {
                # 💡 FIX 2: Explicitly round and save the pure float values
                "actual_price": round(actual_price_raw, 2),
                "prediction_error_pct": round(error_pct_raw, 2)
            }
        }
        
        # Update the single document using its unique _id
        predictions_collection.update_one(
            {"_id": pred['_id']}, 
            update_operation
        )
        # 💡 FIX 3: Update print statement to use the rounded values
        print(f"Updated {ticker} ({target_date_str}): Actual: ${round(actual_price_raw, 2)}, Error: {round(error_pct_raw, 2)}%")

    print("Tracking: Actual price update complete.")
