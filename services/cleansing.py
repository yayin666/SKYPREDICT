import pandas as pd
from services.route_standardizer import standardize_route

def clean_and_aggregate_data(df):
    """
    Takes the raw flight-level dataset, cleans it, and aggregates to monthly level.
    """
    # 1. Standardize route names
    df[['route_id', 'origin_iata', 'dest_iata']] = df.apply(
        lambda row: pd.Series(standardize_route(row['Departure_City'], row['Arrival_City'])), axis=1
    )
    
    # 2. Ensure date is datetime and extract period_month (1st of the month)
    df['Date'] = pd.to_datetime(df['Date'])
    df['period_month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    
    # 3. Aggregate data to monthly level per route
    monthly_df = df.groupby(['route_id', 'period_month']).agg({
        'Passengers': 'sum',
        'Seat_Capacity': 'sum',
        'Revenue_USD': 'sum',
        'origin_iata': 'first',
        'dest_iata': 'first',
        'Departure_City': 'first',
        'Arrival_City': 'first',
        'Route_Type': 'first'
    }).reset_index()
    
    # 4. Calculate Load Factor
    monthly_df['load_factor'] = monthly_df['Passengers'] / monthly_df['Seat_Capacity']
    
    # Rename columns to match database models
    monthly_df = monthly_df.rename(columns={
        'Passengers': 'passenger_count',
        'Seat_Capacity': 'available_seats',
        'Revenue_USD': 'revenue',
        'Departure_City': 'origin_city',
        'Arrival_City': 'destination_city',
        'Route_Type': 'region'
    })
    
    return monthly_df

