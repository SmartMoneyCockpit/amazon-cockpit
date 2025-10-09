from __future__ import annotations
class SheetsClient:
  def __init__(self,*a,**k): self.available=False; self.reason='gspread not installed or Google credentials not configured'
  def test_connection(self): return {'ok':False,'reason':self.reason}
