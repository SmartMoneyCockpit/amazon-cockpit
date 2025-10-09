from services.amazon_ads_service import get_profiles,_db
try:
 print(len(get_profiles()))
except Exception as e:
 print('Auth fail',e)
con=_db(); con.execute('select 1'); con.close()
print('Health OK')
