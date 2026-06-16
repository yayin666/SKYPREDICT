import pandas as pd

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Imputes or drops missing values based on FR-104 (Missing Value Imputation).
    - Drops rows with missing critical identifiers.
    - Imputes numerical metrics with mean/median if missing.
    """
    df = df.copy()
    
    # Drop rows if Date, Departure_City, or Arrival_City are missing
    critical_cols = ['Date', 'Departure_City', 'Arrival_City']
    df = df.dropna(subset=critical_cols)
    
    # Impute missing numerical data with the median
    numerical_cols = ['Passengers', 'Seat_Capacity', 'Revenue_USD']
    for col in numerical_cols:
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            
    return df
