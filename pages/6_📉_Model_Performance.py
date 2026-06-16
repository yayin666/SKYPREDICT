import streamlit as st
import pandas as pd
import plotly.express as px
from database.connection import SessionLocal
from database.models import Forecast

st.set_page_config(page_title="Model Performance", page_icon="📉", layout="wide")
st.title("📉 Model Performance Dashboard")
st.markdown("System-wide overview of Machine Learning forecast accuracy.")

db = SessionLocal()
all_forecasts = db.query(Forecast).filter(Forecast.mape.isnot(None)).all()

if not all_forecasts:
    st.warning("No accuracy metrics found. Run an AI Forecast first!")
    db.close()
    st.stop()

route_metrics = {}
for f in all_forecasts:
    if f.route_id not in route_metrics:
        route_metrics[f.route_id] = {
            'Route': f.route_id,
            'Model': f.model_type,
            'MAPE (%)': float(f.mape) * 100,
            'RMSE': float(f.rmse) if f.rmse else 0.0,
            'MAE': float(f.mae) if f.mae else 0.0
        }

df = pd.DataFrame(list(route_metrics.values()))
if df.empty:
    st.stop()

st.markdown("### 🌐 System-Wide Accuracy")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg MAPE", f"{df['MAPE (%)'].mean():.2f}%")
c2.metric("Avg RMSE", f"{df['RMSE'].mean():.1f}")
c3.metric("Avg MAE", f"{df['MAE'].mean():.1f}")
worst = df.loc[df['MAPE (%)'].idxmax()]
c4.metric(f"Worst Route ({worst['Route']})", f"{worst['MAPE (%)']:.2f}%", delta="Review Needed", delta_color="inverse")

st.markdown("---")
st.subheader("📊 Route Accuracy Ranking")
df = df.sort_values(by='MAPE (%)', ascending=False)
fig = px.bar(df, x='Route', y='MAPE (%)', color='MAPE (%)', color_continuous_scale=['green', 'yellow', 'red'], text_auto='.2f', hover_data=['Model', 'RMSE', 'MAE'])
fig.update_layout(template="plotly_white", xaxis_title="Flight Route", yaxis_title="Error Margin (MAPE %)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📋 Detailed Metrics Table")
st.dataframe(df.style.background_gradient(subset=['MAPE (%)'], cmap='Reds'), use_container_width=True)
db.close()
