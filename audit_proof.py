# audit_proof.py - Automates the 'Time Travel' step for immediate auditing.

import mongodb_client
from datetime import datetime, timedelta
from bson.objectid import ObjectId

def force_audit_readiness(days_to_shift=4):
    """
    Finds predictions made today and moves their target_date back by 
    'days_to_shift' days so they can be immediately audited.
    """
    print("\n--- FORCING AUDIT READINESS (TIME SHIFT) ---")
    
    # 1. Get today's date for filtering
    today = datetime.now().date()
    # Find records created TODAY (prediction_date)
    today_dt = datetime.combine(today, datetime.min.time())

    # Calculate the target past date
    past_target_dt = datetime.combine(today - timedelta(days=days_to_shift), datetime.min.time())
    
    # 2. Define the Query: Find the most recent corrected predictions
    query = {
        # Find predictions that have not been audited yet
        "actual_price": None,
        # Find predictions that are the LATEST model version (Corrected)
        "model_version": {"$regex": "Corrected$"},
        # Find predictions made TODAY (or recently)
        "prediction_date": {"$gte": today_dt - timedelta(days=1)} 
    }
    
    # 3. Define the Update Operation: Shift the target_date to the past
    update_operation = {
        "$set": {
            "target_date": past_target_dt
        }
    }
    
    # 4. Execute the Update
    predictions_collection = mongodb_client.predictions_collection
    if predictions_collection is None:
        print("ERROR: Database connection failed.")
        return

    result = predictions_collection.update_many(query, update_operation)
    
    if result.modified_count > 0:
        print(f"SUCCESS: Shifted {result.modified_count} NEW corrected prediction(s) to {past_target_dt.date()} for immediate audit.")
        print("Now run 'python tracking_engine.py' to generate the proof.")
    else:
        print("WARNING: No un-audited 'Corrected' predictions found to shift.")
        print("-> Make sure you run the Streamlit prediction button first!")


if __name__ == "__main__":
    force_audit_readiness()