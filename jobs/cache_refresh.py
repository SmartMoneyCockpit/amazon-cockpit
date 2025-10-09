from services.amazon_ads_service import fetch_metrics
from datetime import date,timedelta
rows=fetch_metrics(date.today()-timedelta(days=34),date.today())
print('Cache rows:',len(rows))
