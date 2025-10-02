
"""Catalog Items enrichment (SP-API) with safe fallbacks.
- If sp-api lib + creds exist: fetch title/brand/category/dimensions for given ASINs.
- Cache results to Google Sheets tab `catalog_cache` via sheets_writer.
"""
from __future__ import annotations
import pandas as pd

try:
    from sp_api.api import CatalogItems
    from sp_api.base import Marketplaces
    HAVE_LIB = True
except Exception:
    HAVE_LIB = False

from utils.sp_config import CONFIG
from utils.sheets_writer import write_df

def _client_kwargs():
    return dict(
        refresh_token=CONFIG.get("refresh_token"),
        lwa_app_id=CONFIG.get("lwa_app_id"),
        lwa_client_secret=CONFIG.get("lwa_client_secret"),
        aws_access_key=CONFIG.get("aws_access_key"),
        aws_secret_key=CONFIG.get("aws_secret_key"),
        role_arn=CONFIG.get("role_arn"),
        marketplace=Marketplaces.US,
    )

def enrich_asins(asins: list[str]) -> pd.DataFrame:
    asins = [a for a in asins if a]
    rows = []
    if HAVE_LIB and asins:
        try:
            ci = CatalogItems(**_client_kwargs())
            for asin in asins:
                try:
                    res = ci.get_catalog_item(asin, MarketplaceIds=CONFIG['marketplace_ids']).payload or {}
                    attr = res.get("attributeSets", [{}])[0] if res.get("attributeSets") else {}
                    rows.append(dict(
                        asin=asin,
                        title=res.get("Summaries",[{}])[0].get("ItemName") if res.get("Summaries") else None,
                        brand=attr.get("brand"),
                        category=(attr.get("productTypeName") or attr.get("itemTypeName")),
                        weight_kg=(attr.get("itemDimensions") or {}).get("itemWeight",{}).get("value"),
                        size=(attr.get("size") or None),
                    ))
                except Exception:
                    rows.append(dict(asin=asin))
        except Exception:
            pass
    df = pd.DataFrame(rows)
    if not df.empty:
        write_df("catalog_cache", df, clear=False)
    return df
