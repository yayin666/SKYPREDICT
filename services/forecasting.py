from utils.logger import log_event, log_error
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import adfuller
from sqlalchemy.orm import Session
from database.models import MonthlyMetric, Forecast
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings("ignore")

def check_stationarity(series):
    try:
        result = adfuller(series.dropna())
        return result[1] <= 0.05
    except:
        return False

def calculate_mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    if not mask.any(): return 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask]))

def generate_forecast(db: Session, route_id: str, months_ahead: int = 6):
    metrics = db.query(MonthlyMetric).filter(MonthlyMetric.route_id == route_id).order_by(MonthlyMetric.period_month).all()
    if not metrics:
        return False, "No historical data found for this route."
        
    df = pd.DataFrame([{'period_month': m.period_month, 'passenger_count': m.passenger_count} for m in metrics])
    df.set_index('period_month', inplace=True)
    df.index = pd.to_datetime(df.index)
    df = df.groupby(level=0).sum()
    df = df.asfreq('MS')
    df['passenger_count'] = df['passenger_count'].interpolate(method='linear')
    
    n_records = len(df)
    if n_records < 6: return False, "Insufficient data to forecast (minimum 6 months required)."
    y = df['passenger_count']
    
    mape_score, rmse_score, mae_score = None, None, None
    if n_records >= 12:
        try:
            train, test = y[:-3], y[-3:]
            if len(train) >= 24:
                d = 0 if check_stationarity(train) else 1
                bt_model = SARIMAX(train, order=(1, d, 1), seasonal_order=(1, 1, 0, 12), enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
                preds = bt_model.get_forecast(steps=3).predicted_mean
            else:
                bt_model = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=min(12, len(train)//2)).fit()
                preds = bt_model.forecast(3)
            mape_score = calculate_mape(test, preds)
            rmse_score = np.sqrt(mean_squared_error(test, preds))
            mae_score = mean_absolute_error(test, preds)
        except Exception:
            pass
            
    model_used = ""
    forecast_values = []
    lb_95, ub_95 = [], []
    lb_80, ub_80 = [], []
    
    if n_records >= 24:
        model_used = "SARIMA"
        try:
            d = 0 if check_stationarity(y) else 1
            model = SARIMAX(y, order=(1, d, 1), seasonal_order=(1, 1, 0, 12), enforce_stationarity=False, enforce_invertibility=False)
            results = model.fit(disp=False)
            forecast = results.get_forecast(steps=months_ahead)
            forecast_values = forecast.predicted_mean.values
            
            ci_95 = forecast.conf_int(alpha=0.05)
            lb_95, ub_95 = ci_95.iloc[:, 0].values, ci_95.iloc[:, 1].values
            
            ci_80 = forecast.conf_int(alpha=0.20)
            lb_80, ub_80 = ci_80.iloc[:, 0].values, ci_80.iloc[:, 1].values
        except Exception as e:
            model_used = "Exponential Smoothing (Fallback)"
            model = ExponentialSmoothing(y, trend='add', seasonal='add', seasonal_periods=12).fit()
            forecast_values = model.forecast(months_ahead).values
            std_error = np.std(model.resid)
            lb_95, ub_95 = forecast_values - (1.96 * std_error), forecast_values + (1.96 * std_error)
            lb_80, ub_80 = forecast_values - (1.28 * std_error), forecast_values + (1.28 * std_error)
    else:
        model_used = "Exponential Smoothing"
        trend_type = 'add' if n_records >= 12 else None
        seasonal_type = 'add' if n_records >= 12 else None
        periods = 12 if n_records >= 12 else None
        
        try:
            model = ExponentialSmoothing(y, trend=trend_type, seasonal=seasonal_type, seasonal_periods=periods).fit()
            forecast_values = model.forecast(months_ahead).values
            std_error = np.std(model.resid)
            lb_95, ub_95 = forecast_values - (1.96 * std_error), forecast_values + (1.96 * std_error)
            lb_80, ub_80 = forecast_values - (1.28 * std_error), forecast_values + (1.28 * std_error)
        except:
            model_used = "Simple Moving Average"
            sma_value = y.tail(6).mean()
            forecast_values = np.array([sma_value] * months_ahead)
            std_error = np.std(y)
            lb_95, ub_95 = forecast_values - (1.96 * std_error), forecast_values + (1.96 * std_error)
            lb_80, ub_80 = forecast_values - (1.28 * std_error), forecast_values + (1.28 * std_error)
            
    db.query(Forecast).filter(Forecast.route_id == route_id).delete()
    
    last_date = y.index[-1]
    new_records = []
    for i in range(months_ahead):
        db_mape = float(np.clip(mape_score, 0, 9.9999)) if mape_score is not None else None
        db_rmse = float(rmse_score) if rmse_score is not None else None
        db_mae = float(mae_score) if mae_score is not None else None
        
        f = Forecast(
            route_id=route_id, forecast_month=last_date + relativedelta(months=i+1), 
            point_forecast=max(0, int(forecast_values[i])), 
            ci_lower_95=max(0, int(lb_95[i])), ci_upper_95=max(0, int(ub_95[i])), 
            ci_lower_80=max(0, int(lb_80[i])), ci_upper_80=max(0, int(ub_80[i])), 
            model_type=model_used, mape=db_mape, rmse=db_rmse, mae=db_mae
        )
        new_records.append(f)
        
    db.add_all(new_records)
    db.commit()
    return True, f"Forecast generated successfully using {model_used}."
