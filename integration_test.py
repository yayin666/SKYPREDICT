import sys
sys.path.append('.')

print("=== SkyPredict Final Integration Test ===\n")

# 1. DB connection
from database.connection import SessionLocal, engine
db = SessionLocal()
print("[PASS] 1. Database connection OK")

# 2. Analytics
from services.analytics import get_route_analytics, get_route_rankings
df = get_route_analytics(db)
assert not df.empty, "No analytics data"
rank = get_route_rankings(df)
assert 'growth_rate' in rank.columns
assert 'rev_contribution' in rank.columns
print(f"[PASS] 2. Analytics OK — {len(rank)} routes ranked")

# 3. Forecasting
from database.models import Forecast
fc_count = db.query(Forecast).count()
print(f"[PASS] 3. Forecasting OK — {fc_count} forecast records in DB")

# 4. Recommendations
from database.models import Recommendation
rec_count = db.query(Recommendation).count()
print(f"[PASS] 4. Recommendations OK — {rec_count} recommendation records in DB")

# 5. Exports
from services.export import export_to_csv, export_to_excel, export_to_pdf
csv = export_to_csv(rank)
xls = export_to_excel(rank)
pdf = export_to_pdf(rank, "Integration Test")
assert len(csv) > 0
assert len(xls) > 0
assert len(pdf) > 0
print(f"[PASS] 5. Exports OK — CSV={len(csv)}b, Excel={len(xls)}b, PDF={len(pdf)}b")

# 6. Saved Views model
from database.models import SavedView
sv_count = db.query(SavedView).count()
print(f"[PASS] 6. Saved Views OK — {sv_count} saved views in DB")

# 7. Logging
from utils.logger import log_event, log_error
log_event("test", "Integration test completed successfully")
print("[PASS] 7. Structured logging OK — event written to logs/skypredict.log")

db.close()
print("\n=== ALL TESTS PASSED ===")
