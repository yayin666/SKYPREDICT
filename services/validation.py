import pandas as pd

def validate_schema(df: pd.DataFrame) -> bool:
    """
    Ensures the uploaded dataset matches the required schema for Phase 1.
    """
    required_columns = [
        'Date', 'Departure_City', 'Arrival_City', 
        'Passengers', 'Seat_Capacity', 'Revenue_USD'
    ]
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")
        
    return True
