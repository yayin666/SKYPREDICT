import streamlit as st
import pandas as pd
import plotly.express as px
import json
from database.connection import SessionLocal
from services.analytics import get_route_analytics, get_route_rankings
from services.export import export_to_csv
from database.models import SavedView

st.set_page_config(page_title="Route Analytics", page_icon="🗺️", layout="wide")
st.title("🗺️ Route Analytics")

db = SessionLocal()

# --- Saved Views (FR-506) ---
with st.sidebar:
    st.header("📁 Saved Views")
    views = db.query(SavedView).filter(SavedView.page == 'analytics').all()
    view_names = ["(None)"] + [v.name for v in views]
    selected_view = st.selectbox("Load a saved view", view_names)

    if selected_view != "(None)":
        view_obj = next((v for v in views if v.name == selected_view), None)
        if view_obj and view_obj.filters:
            loaded_filters = json.loads(view_obj.filters)
        else:
            loaded_filters = {}
        if st.button("🗑️ Delete View"):
            db.query(SavedView).filter(SavedView.name == selected_view).delete()
            db.commit()
            st.success(f"Deleted '{selected_view}'")
            st.rerun()
    else:
        loaded_filters = {}

    st.markdown("---")
    st.header("🔍 Filters")

@st.cache_data(ttl=3600)
def load_raw():
    _db = SessionLocal()
    d = get_route_analytics(_db)
    _db.close()
    return d

raw_df = load_raw()
if raw_df.empty:
    st.info("No data found. Please upload data on the Data Management page.")
    db.close()
    st.stop()

min_date, max_date = raw_df['period_month'].min(), raw_df['period_month'].max()
if hasattr(min_date, 'date'):
    min_date, max_date = min_date.date(), max_date.date()

with st.sidebar:
    regions = ['All'] + list(raw_df['region'].unique())
    region_default = loaded_filters.get('region', 'All')
    region_idx = regions.index(region_default) if region_default in regions else 0
    region = st.selectbox("Region", regions, index=region_idx)

    date_range = st.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

    view_name_input = st.text_input("Save current view as:")
    if st.button("💾 Save View") and view_name_input:
        filter_cfg = json.dumps({'region': region, 'start': str(date_range[0]), 'end': str(date_range[1])})
        existing = db.query(SavedView).filter(SavedView.name == view_name_input).first()
        if existing:
            existing.filters = filter_cfg
        else:
            db.add(SavedView(name=view_name_input, page='analytics', filters=filter_cfg))
        db.commit()
        st.success(f"Saved view '{view_name_input}'")
        st.rerun()

start_d = date_range[0] if len(date_range) >= 1 else min_date
end_d   = date_range[1] if len(date_range) >= 2 else max_date

filtered_df = raw_df.copy()
if region != 'All':
    filtered_df = filtered_df[filtered_df['region'] == region]
filtered_df = filtered_df[
    (filtered_df['period_month'] >= start_d) &
    (filtered_df['period_month'] <= end_d)
]

rank_df = get_route_rankings(filtered_df)

if rank_df.empty:
    st.warning("No data for this filter.")
    db.close()
    st.stop()

# --- KPIs ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("Routes", len(rank_df))
k2.metric("Total Passengers", f"{rank_df['passengers'].sum():,.0f}")
k3.metric("Total Revenue", f"${rank_df['revenue'].sum():,.0f}")
sys_lf = (rank_df['passengers'].sum() / rank_df['seats'].sum() * 100) if rank_df['seats'].sum() > 0 else 0
k4.metric("Avg System Load Factor", f"{sys_lf:.1f}%")

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📊 Rankings", "📈 Load Factor vs Growth", "🔀 Route Comparison"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        top_revenue = rank_df.sort_values('revenue', ascending=False).head(10)
        fig = px.bar(top_revenue, x='route_id', y='revenue', color='region',
                     title="Top 10 Routes by Revenue", labels={'revenue': 'Revenue (USD)'})
        st.plotly_chart(fig, use_container_width=True)

        # Pareto
        pareto = rank_df.sort_values('revenue', ascending=False).copy()
        pareto['cum_pct'] = pareto['revenue'].cumsum() / pareto['revenue'].sum() * 100
        fig3 = px.bar(pareto, x='route_id', y='rev_contribution',
                      title="Revenue Contribution % (Pareto)",
                      labels={'rev_contribution': '% of Total Revenue'})
        fig3.add_scatter(x=pareto['route_id'], y=pareto['cum_pct'], mode='lines+markers',
                         name='Cumulative %', yaxis='y2')
        fig3.update_layout(yaxis2=dict(overlaying='y', side='right', title='Cumulative %'))
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        disp = rank_df[['route_id','origin','dest','region','passengers','avg_load_factor','growth_rate','rev_contribution']].copy()
        disp['avg_load_factor'] = (disp['avg_load_factor'] * 100).round(1)
        disp['growth_rate'] = disp['growth_rate'].round(1)
        disp['rev_contribution'] = disp['rev_contribution'].round(2)
        disp.columns = ['Route','Origin','Dest','Region','Passengers','LF %','Growth %','Rev %']

        def color_growth(val):
            color = 'green' if val > 0 else 'red'
            return f'color: {color}'

        st.dataframe(disp.style.map(color_growth, subset=['Growth %']), use_container_width=True)
        st.download_button("📥 Export CSV", export_to_csv(rank_df), "route_rankings.csv", "text/csv")

with tab2:
    fig2 = px.scatter(rank_df, x='growth_rate', y='avg_load_factor',
                      size='revenue', color='region', hover_name='route_id',
                      title="Load Factor vs. Growth Rate (bubble = revenue)",
                      labels={'growth_rate': 'Growth Rate %', 'avg_load_factor': 'Load Factor (0-1)'})
    fig2.add_hline(y=0.85, line_dash="dash", line_color="red", annotation_text="LF Capacity Warning (85%)")
    fig2.add_hline(y=0.60, line_dash="dash", line_color="orange", annotation_text="LF Underperformance (60%)")
    fig2.add_vline(x=0,    line_dash="dash", line_color="grey", annotation_text="Zero Growth")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown("#### Compare routes side-by-side")
    all_routes = list(rank_df['route_id'])
    selected_routes = st.multiselect("Select 2–4 routes to compare", all_routes, default=all_routes[:2])
    if len(selected_routes) >= 2:
        comp = rank_df[rank_df['route_id'].isin(selected_routes)][
            ['route_id','passengers','revenue','avg_load_factor','growth_rate','rev_contribution']
        ].copy()
        comp['avg_load_factor'] = (comp['avg_load_factor'] * 100).round(1)
        comp['growth_rate'] = comp['growth_rate'].round(1)
        comp.columns = ['Route','Passengers','Revenue','LF %','Growth %','Rev %']
        st.dataframe(comp, use_container_width=True)
        fig_comp = px.bar(comp.melt(id_vars='Route', value_vars=['Passengers','LF %','Growth %']),
                          x='Route', y='value', color='variable', barmode='group',
                          title="Side-by-side Comparison")
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("Select at least 2 routes to compare.")

db.close()
