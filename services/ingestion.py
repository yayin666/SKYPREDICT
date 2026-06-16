from utils.logger import log_event, log_error
import pandas as pd
from sqlalchemy.orm import Session
from database.models import Route, MonthlyMetric, IngestionLog
from services.validation import validate_schema
from services.imputation import handle_missing_values
from services.cleansing import clean_and_aggregate_data

def ingest_file(db: Session, file_path_or_buffer, filename: str):
    if filename.endswith('.csv'):
        df = pd.read_csv(file_path_or_buffer)
    else:
        df = pd.read_excel(file_path_or_buffer)
        
    total_raw = len(df)
    
    try:
        # Pipeline execution
        validate_schema(df)
        df = handle_missing_values(df)
        monthly_df = clean_and_aggregate_data(df)
        
        unique_routes = monthly_df[['route_id', 'origin_iata', 'dest_iata', 'origin_city', 'destination_city', 'region']].drop_duplicates(subset=['route_id'])
        for _, r in unique_routes.iterrows():
            existing_route = db.query(Route).filter(Route.route_id == r['route_id']).first()
            if not existing_route:
                new_route = Route(
                    route_id=r['route_id'],
                    origin_iata=r['origin_iata'],
                    destination_iata=r['dest_iata'],
                    origin_city=r['origin_city'],
                    destination_city=r['destination_city'],
                    region=r['region']
                )
                db.add(new_route)
        db.flush() 
        
        route_ids = unique_routes['route_id'].tolist()
        db.query(MonthlyMetric).filter(MonthlyMetric.route_id.in_(route_ids)).delete()
        
        records = []
        for _, row in monthly_df.iterrows():
            metric = MonthlyMetric(
                route_id=row['route_id'],
                period_month=row['period_month'],
                passenger_count=row['passenger_count'],
                available_seats=row['available_seats'],
                revenue=row['revenue'],
                load_factor=row['load_factor']
            )
            records.append(metric)
            
        db.add_all(records)
        
        log = IngestionLog(filename=filename, total_records=total_raw, valid_records=total_raw, rejected_records=0, status="Success")
        db.add(log)
        db.commit()
        log_event('ingestion', 'Data ingested successfully')
        return True, f"Successfully processed {total_raw} daily flights into {len(records)} monthly route metrics."
        
    except Exception as e:
        db.rollback()
        log_error(f"Ingestion failed: {str(e)}")
        log = IngestionLog(filename=filename, total_records=total_raw, valid_records=0, rejected_records=total_raw, status="Failed")
        db.add(log)
        db.commit()
        return False, f"Database insertion failed: {str(e)}"
