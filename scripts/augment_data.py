import pandas as pd
import numpy as np

def augment_data():
    input_file = 'PIA_2026_Advanced_Kaggle_Dataset.csv'
    output_file = 'data/raw/PIA_2026_Augmented.csv'
    
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    
    # Ensure Date is parsed as datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    print("Generating Year -1 data...")
    df_minus_1 = df.copy()
    df_minus_1['Date'] = df_minus_1['Date'] - pd.DateOffset(years=1)
    df_minus_1['Year'] = df_minus_1['Date'].dt.year
    noise_1 = np.random.uniform(0.92, 0.98, len(df_minus_1)) # 2-8% reduction
    df_minus_1['Passengers'] = (df_minus_1['Passengers'] * noise_1).astype(int)
    df_minus_1['Revenue_USD'] = df_minus_1['Revenue_USD'] * noise_1
    df_minus_1['Load_Factor_%'] = (df_minus_1['Passengers'] / df_minus_1['Seat_Capacity']) * 100
    
    print("Generating Year -2 data...")
    df_minus_2 = df.copy()
    df_minus_2['Date'] = df_minus_2['Date'] - pd.DateOffset(years=2)
    df_minus_2['Year'] = df_minus_2['Date'].dt.year
    noise_2 = np.random.uniform(0.85, 0.92, len(df_minus_2)) # 8-15% reduction
    df_minus_2['Passengers'] = (df_minus_2['Passengers'] * noise_2).astype(int)
    df_minus_2['Revenue_USD'] = df_minus_2['Revenue_USD'] * noise_2
    df_minus_2['Load_Factor_%'] = (df_minus_2['Passengers'] / df_minus_2['Seat_Capacity']) * 100
    
    print("Combining datasets...")
    final_df = pd.concat([df_minus_2, df_minus_1, df], ignore_index=True)
    
    # Sort by date
    final_df = final_df.sort_values('Date').reset_index(drop=True)
    
    print(f"Saving to {output_file}...")
    final_df.to_csv(output_file, index=False)
    
    print(f"Original records: {len(df)}")
    print(f"Augmented records: {len(final_df)}")
    print("Augmentation complete!")

if __name__ == '__main__':
    augment_data()
