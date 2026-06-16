import streamlit as st
import pandas as pd
import plotly.express as px
from database.connection import SessionLocal
from services.analytics import get_route_analytics, get_route_rankings
from services.export import export_to_csv, export_to_excel, export_to_pdf

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")
st.title("📊 Executive Dashboard")

@st.cache_data(ttl=3600)
def load_data():
    db = SessionLocal()
    df = get_route_analytics(db)
    if not df.empty:
        rank = get_route_rankings(df)
    else:
        rank = pd.DataFrame()
    db.close()
    return df, rank

df, rank_df = load_data()

if df.empty:
    st.info("Welcome to SkyPredict! Please go to the Data Management page to upload your first dataset.")
    st.stop()

# KPIs
total_pax = rank_df['passengers'].sum()
total_rev = rank_df['revenue'].sum()
sys_lf = (rank_df['passengers'].sum() / rank_df['seats'].sum()) * 100 if rank_df['seats'].sum() > 0 else 0

st.subheader("Network KPIs")
c1, c2, c3 = st.columns(3)
c1.metric("Total Passengers", f"{total_pax:,.0f}")
c2.metric("Total Revenue", f"${total_rev:,.2f}")
c3.metric("System Load Factor", f"{sys_lf:.1f}%")

st.markdown("---")
# Network Health
st.subheader("Network Health & Top Routes")
col1, col2 = st.columns(2)

with col1:
    fig1 = px.pie(rank_df.head(5), values='revenue', names='route_id', title="Top 5 Routes by Revenue")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    growing_routes = len(rank_df[rank_df['growth_rate'] > 0])
    total_routes = len(rank_df)
    health_pct = (growing_routes / total_routes) * 100 if total_routes > 0 else 0
    
    fig2 = px.pie(values=[growing_routes, total_routes - growing_routes], names=['Growing', 'Shrinking'], title=f"Network Growth Health ({health_pct:.1f}% Growing)", color_discrete_sequence=['green', 'red'])
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("KPI Monitoring Panel")
col3, col4 = st.columns(2)
with col3:
    if sys_lf > 85:
        st.error(f"🚨 **Critical Alert:** System Load Factor is dangerously high at {sys_lf:.1f}%. Network is at absolute capacity. Consider expanding fleet.")
    elif sys_lf < 60:
        st.warning(f"⚠️ **Warning Alert:** System Load Factor is very poor at {sys_lf:.1f}%. High fuel wastage. Consider reducing fleet capacity.")
    else:
        st.success(f"✅ **Healthy:** System Load Factor is optimal at {sys_lf:.1f}%. Capacity is well-balanced.")
with col4:
    if health_pct < 50:
        st.error(f"🚨 **Critical Alert:** Majority of routes ({100-health_pct:.1f}%) are currently shrinking in passenger demand. Review marketing strategy.")
    else:
        st.success(f"✅ **Healthy:** The majority of network routes ({health_pct:.1f}%) are experiencing positive growth.")

st.markdown("---")
st.subheader("📥 Export Reports")
st.markdown("Download full network performance data for stakeholder reporting.")

d1, d2, d3 = st.columns(3)
with d1:
    st.download_button(label="Download CSV", data=export_to_csv(rank_df), file_name="skypredict_report.csv", mime="text/csv")
with d2:
    st.download_button(label="Download Excel", data=export_to_excel(rank_df), file_name="skypredict_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
with d3:
    st.download_button(label="Download PDF", data=export_to_pdf(rank_df, "Network Rankings"), file_name="skypredict_report.pdf", mime="application/pdf")

