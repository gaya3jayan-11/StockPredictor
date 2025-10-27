from mongodb_client import predictions_collection
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict

def get_avg_predicted_price(ticker: str, days: int = 7) -> List[Dict]:
    start_date = datetime.now() - timedelta(days=days)
    pipeline = [
        #Filter the data by ticker and prediction date
        {"$match": {
            "ticker": ticker,
            "prediction_date": {"$gte": start_date} 
        }},
        #Group the matching predictions
        {"$group": {
            "_id": "$ticker", 
            "average_predicted_price": {"$avg": "$predicted_price"}, 
            "prediction_count": {"$sum": 1} 
        }},
        #Clean up and format the output
        {"$project": {
            "_id": 0, 
            "ticker": "$_id",
            "average_predicted_price": {"$round": ["$average_predicted_price", 2]},
            "prediction_count": 1
        }}
    ]
    return list(predictions_collection.aggregate(pipeline))

def get_historical_accuracy(ticker: str) -> pd.DataFrame:
    pipeline = [
        #Include records where accuracy has been calculated
        {"$match": {
            "ticker": ticker,
            "prediction_error_pct": {"$ne": None} 
        }},
        #Sort by the date the price was recorded
        {"$sort": {
            "target_date": 1 
        }},
        {"$project": {
            "_id": 0,
            "Date": "$target_date", 
            "Predicted Price": "$predicted_price",
            "Actual Price": "$actual_price",
            "Error Percentage": "$prediction_error_pct"
        }}
    ]
    
    results = list(predictions_collection.aggregate(pipeline))
    
    return pd.DataFrame(results) if results else pd.DataFrame()
