from sqlalchemy import Column, Integer, String, Boolean, Date, Numeric, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class RecommendationType(enum.Enum):
    INCREASE_FREQUENCY = "Increase Frequency"
    REDUCE_CAPACITY = "Reduce Capacity"
    UPGRADE_AIRCRAFT = "Upgrade Aircraft"
    REVIEW_PROFITABILITY = "Review Profitability"
    EXPAND_ROUTE = "Expand Route"
    MONITOR = "Monitor"

class Route(Base):
    __tablename__ = 'routes'

    route_id = Column(String(10), primary_key=True) # e.g., BOM-DEL
    origin_iata = Column(String(3), nullable=False)
    destination_iata = Column(String(3), nullable=False)
    origin_city = Column(String(100))
    destination_city = Column(String(100))
    region = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    metrics = relationship("MonthlyMetric", back_populates="route")
    forecasts = relationship("Forecast", back_populates="route")
    recommendations = relationship("Recommendation", back_populates="route")

class MonthlyMetric(Base):
    __tablename__ = 'monthly_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String(10), ForeignKey('routes.route_id'))
    period_month = Column(Date, nullable=False)
    passenger_count = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=True)
    revenue = Column(Numeric(12, 2), nullable=True)
    load_factor = Column(Numeric(5, 4), nullable=True) # Computed
    ingested_at = Column(DateTime, default=datetime.utcnow)

    route = relationship("Route", back_populates="metrics")

class Forecast(Base):
    __tablename__ = 'forecasts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String(10), ForeignKey('routes.route_id'))
    forecast_month = Column(Date, nullable=False)
    point_forecast = Column(Numeric(10, 2))
    ci_lower_80 = Column(Numeric(10, 2))
    ci_upper_80 = Column(Numeric(10, 2))
    ci_lower_95 = Column(Numeric(10, 2))
    ci_upper_95 = Column(Numeric(10, 2))
    model_type = Column(String(50))
    model_version = Column(String(50))
    mape = Column(Numeric(5, 4), nullable=True)
    rmse = Column(Numeric(10, 2), nullable=True)
    mae = Column(Numeric(10, 2), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    route = relationship("Route", back_populates="forecasts")

class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String(10), ForeignKey('routes.route_id'))
    recommendation_type = Column(Enum(RecommendationType))
    rationale = Column(Text)
    confidence_level = Column(String(20))
    valid_from = Column(Date)
    valid_until = Column(Date)
    generated_at = Column(DateTime, default=datetime.utcnow)

    route = relationship("Route", back_populates="recommendations")

class IngestionLog(Base):
    __tablename__ = 'ingestion_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255))
    upload_time = Column(DateTime, default=datetime.utcnow)
    total_records = Column(Integer)
    valid_records = Column(Integer)
    rejected_records = Column(Integer)
    status = Column(String(50))





class SavedView(Base):
    __tablename__ = 'saved_views'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    page = Column(String(50), nullable=False)  # e.g. 'analytics', 'executive'
    filters = Column(Text, nullable=True)  # JSON-encoded filter config
    created_at = Column(DateTime, default=datetime.utcnow)
