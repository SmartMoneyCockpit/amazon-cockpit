from services.amazon_ads_service import fetch_metrics
from datetime import date,timedelta
rows=fetch_metrics(date.today()-timedelta(days=6),date.today())
print('Daily rows:',len(rows))
