import pandas as pd
from sqlalchemy.orm import Session
from database.models import Recommendation, Route, RecommendationType
from datetime import datetime

def generate_recommendations(db: Session, rank_df: pd.DataFrame):
    if rank_df.empty: return False, "No data to analyze."
    
    db.query(Recommendation).delete()
    
    new_recs = []
    now = datetime.utcnow()
    
    for _, row in rank_df.iterrows():
        route_id = row['route_id']
        lf = row['avg_load_factor'] * 100
        growth = row['growth_rate']
        
        rec_type = RecommendationType.MONITOR
        rationale = f"Route is performing stably with {lf:.1f}% load factor and {growth:.1f}% growth."
        conf = "Low"
        
        if lf > 85 and growth > 10:
            rec_type = RecommendationType.UPGRADE_AIRCRAFT
            rationale = f"High capacity utilization ({lf:.1f}%) combined with strong growth ({growth:.1f}%) indicates demand is outstripping current aircraft size."
            conf = "High"
        elif lf > 85 and growth > 0:
            rec_type = RecommendationType.INCREASE_FREQUENCY
            rationale = f"Consistent high load factor ({lf:.1f}%) and positive growth ({growth:.1f}%). Adding another flight time is recommended."
            conf = "Medium"
        elif growth > 15 and lf < 85:
            rec_type = RecommendationType.EXPAND_ROUTE
            rationale = f"Exceptional growth ({growth:.1f}%) suggests this route is gaining popularity. Market aggressively to fill remaining {100-lf:.1f}% capacity."
            conf = "Medium"
        elif lf < 60:
            rec_type = RecommendationType.REDUCE_CAPACITY
            rationale = f"Poor load factor ({lf:.1f}%) is burning unnecessary fuel. Consider downgauging aircraft or reducing frequency."
            conf = "High"
        elif row['revenue'] > 0 and row['rev_contribution'] < 0.5 and growth < 0:
            rec_type = RecommendationType.REVIEW_PROFITABILITY
            rationale = f"Route contributes less than 0.5% of network revenue and is shrinking ({growth:.1f}%). Audit for potential cancellation."
            conf = "Medium"
            
        rec = Recommendation(
            route_id=route_id,
            recommendation_type=rec_type,
            rationale=rationale,
            confidence_level=conf,
            valid_from=now.date(),
            generated_at=now
        )
        new_recs.append(rec)
        
    db.add_all(new_recs)
    db.commit()
    return True, f"Generated {len(new_recs)} recommendations."
    
def get_recommendations(db: Session):
    return db.query(Recommendation, Route).join(Route, Recommendation.route_id == Route.route_id).all()
