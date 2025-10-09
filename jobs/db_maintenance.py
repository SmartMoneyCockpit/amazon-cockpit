import sqlite3,os
DB=os.path.join(os.getenv('VEGA_DATA_DIR','/data'),'vega_ads.db')
con=sqlite3.connect(DB); con.execute('VACUUM'); con.close(); print('Vacuumed')
