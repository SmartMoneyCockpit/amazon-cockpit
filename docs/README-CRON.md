A1 14:00 UTC: python jobs/report_daily.py
A2 03:00 UTC: python jobs/cache_refresh.py
A3 04:00 UTC: python jobs/search_terms_daily.py
A4 04:30 UTC: python jobs/placements_daily.py
A5 @hourly   : python jobs/health_check.py
A6 Sun 05:00 : python jobs/db_maintenance.py
A7 Daily 05:10: python jobs/backup_db.py
