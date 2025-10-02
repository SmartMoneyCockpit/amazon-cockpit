
from __future__ import annotations
import pandas as pd
from workers import etl
from utils import finance_exporter
from utils import finance_source
from utils.sheets_writer import write_df

def run_all():
    etl.run_job("refresh_orders_inventory_finances", etl.refresh_orders_inventory_finances)
    etl.run_job("monthly_profitability_rollup", etl.monthly_profitability_rollup)
    df = finance_source.read_profitability_monthly()
    if not df.empty:
        finance_exporter.export_summary_to_sheet(df, tab_name="finance_summary")
    try:
        from utils import sheets_bridge as SB
        kws = SB.read_tab("keywords")
        if isinstance(kws, pd.DataFrame) and not kws.empty:
            write_df("a_plus_snapshot", kws)
    except Exception:
        pass
    return True

if __name__ == "__main__":
    run_all()
