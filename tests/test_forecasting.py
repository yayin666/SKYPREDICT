import sys
import os
sys.path.append(os.getcwd())
import pandas as pd
from services.forecasting import calculate_mape, check_stationarity

def test_calculate_mape():
    y_true = [100, 200, 300]
    y_pred = [110, 190, 330]
    # Errors: 10/100 (10%), 10/200 (5%), 30/300 (10%) -> Mean: 8.33%
    mape = calculate_mape(y_true, y_pred)
    assert round(mape, 4) == 0.0833
    
def test_calculate_mape_zero_division():
    y_true = [0, 200]
    y_pred = [10, 200]
    mape = calculate_mape(y_true, y_pred)
    assert mape == 0.0 # Ignores the zero
    
def test_check_stationarity():
    # A simple linear trend is not stationary
    non_stationary = pd.Series([i for i in range(100)])
    assert check_stationarity(non_stationary) == False

if __name__ == '__main__':
    test_calculate_mape()
    test_calculate_mape_zero_division()
    test_check_stationarity()
    print("All forecasting unit tests passed successfully!")
