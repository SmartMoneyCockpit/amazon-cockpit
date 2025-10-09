import os,gzip,shutil
DB=os.path.join(os.getenv('VEGA_DATA_DIR','/data'),'vega_ads.db'); out=os.path.join(os.getenv('VEGA_DATA_DIR','/data'),'backups'); os.makedirs(out,exist_ok=True)
with open(DB,'rb') as fi, gzip.open(os.path.join(out,'vega_ads-backup.db.gz'),'wb') as fo: shutil.copyfileobj(fi,fo)
print('Backed up')
