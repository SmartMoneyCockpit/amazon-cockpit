
"""SP-API (non-Ads) integration with safe fallbacks.
If the `sp-api` library is installed and credentials exist, we hit live endpoints.
Otherwise we return empty DataFrames so the app never crashes.
"""
from __future__ import annotations
import pandas as pd
from datetime import datetime, timedelta
from . import sp_safety

try:
    # The community Python client
    from sp_api.api import Orders, Finances, FbaInventory, Reports
    from sp_api.api import CatalogItems
    from sp_api.base import Marketplaces, SellingApiException
    HAVE_LIB = True
except Exception:
    HAVE_LIB = False

from utils.sp_config import CONFIG

def _client_kwargs():
    # Map region to Marketplaces.US default; user can extend later
    region = (CONFIG.get("region") or "NA").upper()
    mp = Marketplaces.US
    return dict(
        refresh_token=CONFIG.get("refresh_token"),
        lwa_app_id=CONFIG.get("lwa_app_id"),
        lwa_client_secret=CONFIG.get("lwa_client_secret"),
        aws_access_key=CONFIG.get("aws_access_key"),
        aws_secret_key=CONFIG.get("aws_secret_key"),
        role_arn=CONFIG.get("role_arn"),
        marketplace=mp,
    )

def list_orders(days_back: int = 30) -> pd.DataFrame:
    if not HAVE_LIB or not sp_safety.ready():
        return pd.DataFrame(columns=['order_id','purchase_date','status','sku','asin','qty','price'])
    try:
        after = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
        o = Orders(**_client_kwargs())
        res = o.get_orders(CreatedAfter=after, MarketplaceIds=CONFIG['marketplace_ids']).payload.get('Orders', [])
        rows = []
        for od in res:
            oid = od.get('AmazonOrderId')
            status = od.get('OrderStatus')
            date = od.get('PurchaseDate')
            # Get line items
            it = o.get_order_items(oid).payload.get('OrderItems', [])
            for item in it:
                rows.append(dict(
                    order_id=oid,
                    purchase_date=date,
                    status=status,
                    sku=item.get('SellerSKU'),
                    asin=item.get('ASIN'),
                    qty=item.get('QuantityOrdered'),
                    price=(item.get('ItemPrice', {}) or {}).get('Amount')
                ))
        return pd.DataFrame(rows)
    except Exception as e:
        return pd.DataFrame(columns=['order_id','purchase_date','status','sku','asin','qty','price'])

def list_inventory() -> pd.DataFrame:
    if not HAVE_LIB or not sp_safety.ready():
        return pd.DataFrame(columns=['sku','asin','fnsku','on_hand','available','inbound'])
    try:
        inv = FbaInventory(**_client_kwargs())
        res = inv.get_inventory_summaries(details=True, MarketplaceIds=CONFIG['marketplace_ids']).payload.get('inventorySummaries', [])
        rows = []
        for x in res:
            rows.append(dict(
                sku=x.get('sellerSku'),
                asin=x.get('asin'),
                fnsku=x.get('fnSku'),
                on_hand=x.get('totalQuantity', 0),
                available=(x.get('inventoryDetails', {}) or {}).get('availableQuantity', 0),
                inbound=(x.get('inventoryDetails', {}) or {}).get('inboundWorkingQuantity', 0),
            ))
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame(columns=['sku','asin','fnsku','on_hand','available','inbound'])

def list_finances(days_back: int = 30) -> pd.DataFrame:
    if not HAVE_LIB or not sp_safety.ready():
        return pd.DataFrame(columns=['date','sku','asin','revenue','fees','other'])
    try:
        f = Finances(**_client_kwargs())
        after = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
        res = f.list_financial_events(PostedAfter=after).payload or {}
        # Flatten only shipments and service fees for now
        rows = []
        for sh in (res.get('ShipmentEventList') or []):
            for item in (sh.get('ShipmentItemList') or []):
                rows.append(dict(
                    date=sh.get('PostedDate'),
                    sku=item.get('SellerSKU'),
                    asin=item.get('ASIN'),
                    revenue=(item.get('ItemChargeList', [{}])[0].get('ChargeAmount') or {}).get('Amount', 0),
                    fees=(item.get('ItemFeeList', [{}])[0].get('FeeAmount') or {}).get('Amount', 0),
                    other=0,
                ))
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame(columns=['date','sku','asin','revenue','fees','other'])
