import pandas as pd
from sqlalchemy.orm import Session
from database.models import MonthlyMetric, Route

def get_route_analytics(db: Session, start_date=None, end_date=None, region=None):
    query = db.query(MonthlyMetric, Route).join(Route, MonthlyMetric.route_id == Route.route_id)
    if start_date: query = query.filter(MonthlyMetric.period_month >= start_date)
    if end_date: query = query.filter(MonthlyMetric.period_month <= end_date)
    if region and region != 'All': query = query.filter(Route.region == region)
    
    data = query.all()
    if not data: return pd.DataFrame()
    
    df = pd.DataFrame([{
        'route_id': r.Route.route_id,
        'origin': r.Route.origin_city,
        'dest': r.Route.destination_city,
        'region': r.Route.region,
        'period_month': r.MonthlyMetric.period_month,
        'passengers': r.MonthlyMetric.passenger_count,
        'seats': r.MonthlyMetric.available_seats,
        'revenue': float(r.MonthlyMetric.revenue) if r.MonthlyMetric.revenue else 0.0,
        'load_factor': float(r.MonthlyMetric.load_factor) if r.MonthlyMetric.load_factor else 0.0
    } for r in data])
    
    return df

def get_route_rankings(df: pd.DataFrame):
    if df.empty: return pd.DataFrame()
    
    agg_df = df.groupby(['route_id', 'origin', 'dest', 'region']).agg({
        'passengers': 'sum',
        'seats': 'sum',
        'revenue': 'sum'
    }).reset_index()
    
    agg_df['avg_load_factor'] = (agg_df['passengers'] / agg_df['seats']).fillna(0)
    
    total_rev = agg_df['revenue'].sum()
    agg_df['rev_contribution'] = (agg_df['revenue'] / total_rev) * 100 if total_rev > 0 else 0
    
    growth_data = []
    routes = df['route_id'].unique()
    for route in routes:
        route_data = df[df['route_id'] == route].sort_values('period_month')
        if len(route_data) >= 24:
            last_12 = route_data.tail(12)['passengers'].sum()
            prev_12 = route_data.iloc[-24:-12]['passengers'].sum()
            yoy_growth = ((last_12 - prev_12) / prev_12) * 100 if prev_12 > 0 else 0
        elif len(route_data) >= 2:
            last_month = route_data.iloc[-1]['passengers']
            prev_month = route_data.iloc[-2]['passengers']
            yoy_growth = ((last_month - prev_month) / prev_month) * 100 if prev_month > 0 else 0
        else:
            yoy_growth = 0
        growth_data.append({'route_id': route, 'growth_rate': yoy_growth})
        
    growth_df = pd.DataFrame(growth_data)
    final_df = pd.merge(agg_df, growth_df, on='route_id', how='left')
    
    return final_df.sort_values('passengers', ascending=False)
