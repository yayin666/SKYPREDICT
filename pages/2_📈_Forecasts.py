import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
from database.connection import SessionLocal
from database.models import Route, MonthlyMetric, Forecast
from services.forecasting import generate_forecast

st.set_page_config(page_title="Demand Forecasts", page_icon="📈", layout="wide")
st.title("📈 Demand Forecasting")
st.markdown("Use Machine Learning to predict future passenger demand for any route.")

db = SessionLocal()
routes = db.query(Route).all()
if not routes:
    st.warning("No data found. Upload a dataset first.")
    db.close()
    st.stop()

route_options = {f"{r.route_id} ({r.origin_city} ➔ {r.destination_city})": r.route_id for r in routes}
selected_route_id = route_options[st.selectbox("Select a Route to Forecast", list(route_options.keys()))]

col1, _ = st.columns([1, 1])
with col1:
    months_to_forecast = st.slider("Months to Predict", min_value=1, max_value=24, value=6)

if st.button("🚀 Run AI Forecast", type="primary"):
    with st.spinner("Training Machine Learning Model..."):
        success, msg = generate_forecast(db, selected_route_id, months_ahead=months_to_forecast)
        if success: st.success(msg)
        else: st.error(msg)

metrics = db.query(MonthlyMetric).filter(MonthlyMetric.route_id == selected_route_id).order_by(MonthlyMetric.period_month).all()
forecasts = db.query(Forecast).filter(Forecast.route_id == selected_route_id).order_by(Forecast.forecast_month).all()

if metrics and forecasts:
    hist_df = pd.DataFrame([{'Date': m.period_month, 'Passengers': m.passenger_count} for m in metrics]).groupby('Date', as_index=False).sum()
    fore_df = pd.DataFrame([{'Date': f.forecast_month, 'Passengers': float(f.point_forecast), 'L95': float(f.ci_lower_95), 'U95': float(f.ci_upper_95), 'L80': float(f.ci_lower_80), 'U80': float(f.ci_upper_80), 'Model': f.model_type, 'MAPE': float(f.mape) if f.mape else None, 'RMSE': float(f.rmse) if f.rmse else None, 'MAE': float(f.mae) if f.mae else None} for f in forecasts])
    
    st.markdown("---")
    st.subheader("🤖 Model Performance (Backtesting)")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Architecture", fore_df['Model'].iloc[0])
    
    if pd.notna(fore_df['MAPE'].iloc[0]):
        m_col2.metric("MAPE", f"{fore_df['MAPE'].iloc[0]*100:.2f}%", help="Mean Absolute Percentage Error")
        m_col3.metric("RMSE", f"{fore_df['RMSE'].iloc[0]:.1f}", help="Root Mean Squared Error")
        m_col4.metric("MAE", f"{fore_df['MAE'].iloc[0]:.1f}", help="Mean Absolute Error")
    else:
        m_col2.metric("MAPE", "N/A")
        m_col3.metric("RMSE", "N/A")
        m_col4.metric("MAE", "N/A")
        
    st.subheader("📊 Future Demand Projection")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_df['Date'], y=hist_df['Passengers'], mode='lines+markers', name='Historical Data', line=dict(color='blue', width=2)))
    
    last_hist = hist_df.iloc[-1]
    bridge_x = [last_hist['Date']] + list(fore_df['Date'])
    
    # 95% CI (Lighter)
    bridge_l95 = [last_hist['Passengers']] + list(fore_df['L95'])
    bridge_u95 = [last_hist['Passengers']] + list(fore_df['U95'])
    fig.add_trace(go.Scatter(x=bridge_x + bridge_x[::-1], y=bridge_u95 + bridge_l95[::-1], fill='toself', fillcolor='rgba(255, 0, 0, 0.1)', line=dict(color='rgba(255,255,255,0)'), showlegend=True, name='95% Confidence'))
    
    # 80% CI (Darker)
    bridge_l80 = [last_hist['Passengers']] + list(fore_df['L80'])
    bridge_u80 = [last_hist['Passengers']] + list(fore_df['U80'])
    fig.add_trace(go.Scatter(x=bridge_x + bridge_x[::-1], y=bridge_u80 + bridge_l80[::-1], fill='toself', fillcolor='rgba(255, 0, 0, 0.25)', line=dict(color='rgba(255,255,255,0)'), showlegend=True, name='80% Confidence'))
    
    # Prediction Line
    bridge_y = [last_hist['Passengers']] + list(fore_df['Passengers'])
    fig.add_trace(go.Scatter(x=bridge_x, y=bridge_y, mode='lines+markers', name='AI Prediction', line=dict(color='red', width=2, dash='dash')))
    
    fig.update_layout(xaxis_title="Date", yaxis_title="Total Passengers", hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🧬 Seasonal Trend Decomposition")
    if len(hist_df) >= 24:
        try:
            ts_data = hist_df.set_index('Date')['Passengers'].asfreq('MS').interpolate()
            dec = seasonal_decompose(ts_data, model='additive', period=12)
            f_d = make_subplots(rows=4, cols=1, shared_xaxes=True, subplot_titles=('Observed', 'Trend', 'Seasonal', 'Residual'))
            f_d.add_trace(go.Scatter(x=ts_data.index, y=dec.observed, mode='lines', line=dict(color='black')), row=1, col=1)
            f_d.add_trace(go.Scatter(x=ts_data.index, y=dec.trend, mode='lines', line=dict(color='blue')), row=2, col=1)
            f_d.add_trace(go.Scatter(x=ts_data.index, y=dec.seasonal, mode='lines', line=dict(color='green')), row=3, col=1)
            f_d.add_trace(go.Scatter(x=ts_data.index, y=dec.resid, mode='markers', marker=dict(color='red', size=4)), row=4, col=1)
            f_d.update_layout(height=800, showlegend=False, template="plotly_white")
            st.plotly_chart(f_d, use_container_width=True)
        except Exception as e: st.warning(f"Could not decompose seasonality: {e}")
    else: st.info("Requires 24+ months for decomposition.")

db.close()
