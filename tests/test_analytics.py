import sys
import os
sys.path.append(os.getcwd())
import pandas as pd
from services.analytics import get_route_rankings

def test_get_route_rankings():
    df = pd.DataFrame([
        {'route_id': 'BOM-DEL', 'origin': 'BOM', 'dest': 'DEL', 'region': 'Domestic', 'period_month': '2025-01-01', 'passengers': 1000, 'seats': 1200, 'revenue': 50000},
        {'route_id': 'BOM-DEL', 'origin': 'BOM', 'dest': 'DEL', 'region': 'Domestic', 'period_month': '2025-02-01', 'passengers': 1100, 'seats': 1200, 'revenue': 55000},
        {'route_id': 'JFK-LHR', 'origin': 'JFK', 'dest': 'LHR', 'region': 'International', 'period_month': '2025-01-01', 'passengers': 300, 'seats': 500, 'revenue': 100000}
    ])
    
    rank_df = get_route_rankings(df)
    
    # Assert BOM-DEL
    bom_del = rank_df[rank_df['route_id'] == 'BOM-DEL'].iloc[0]
    assert bom_del['passengers'] == 2100
    assert bom_del['seats'] == 2400
    assert round(bom_del['avg_load_factor'], 4) == 0.875
    assert bom_del['growth_rate'] == 10.0 # 1000 to 1100 is 10%
    
    print("Analytics unit tests passed successfully!")

if __name__ == '__main__':
    test_get_route_rankings()
