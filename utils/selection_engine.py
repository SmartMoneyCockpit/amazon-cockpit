from __future__ import annotations
import math

# Default weights (sum doesn't need to be 1; we normalize final score)
DEFAULT_WEIGHTS = {
    "gross_margin": 3.0,       # (target_price - cost) / target_price
    "avg_star": 2.0,           # 0..5 mapped to 0..1
    "return_rate": -3.0,       # penalize
    "buybox_gap": 1.5,         # (buybox_price - target_price)/target_price if positive
    "keyword_rank": 1.0,       # lower is better -> invert
    "promo_lift": 1.0,
    "roas": 1.0,
    "storage_cost_share": -1.5,
    "forecast_units": 2.0,
    "lead_time": -0.5,         # shorter is better
    "days_of_cover": -0.5,     # too high cover suggests slow mover (penalize)
    "risk_flags": -2.0,        # policy/account health issues -> penalize
}

def _safe_num(v, d=0.0):
    try:
        if v is None or v == "": return d
        return float(v)
    except Exception:
        return d

def _norm_unit(x, lo, hi, invert=False):
    # clamp and scale to 0..1
    if hi == lo: return 0.5
    x = max(lo, min(hi, x))
    val = (x - lo) / (hi - lo)
    return 1.0 - val if invert else val

def score_row(r: dict, weights: dict | None = None) -> tuple[float, dict]:
    w = (weights or DEFAULT_WEIGHTS).copy()
    # Extract inputs (all optional)
    cost = _safe_num(r.get("cost"))
    target_price = _safe_num(r.get("target_price"))
    gross_margin = ((target_price - cost) / target_price) if target_price > 0 else 0.0

    avg_star = _safe_num(r.get("avg_star"))
    return_rate = _safe_num(r.get("return_rate_30d"))
    competitor_price = _safe_num(r.get("competitor_price"))
    buybox_price = _safe_num(r.get("buybox_price"))
    buybox_gap = ((buybox_price - target_price) / target_price) if (target_price > 0 and buybox_price > 0) else 0.0
    keyword_rank = _safe_num(r.get("keyword_rank_avg"))
    promo_lift = _safe_num(r.get("promo_lift_pct"))
    roas = _safe_num(r.get("roas"))
    storage_cost_share = _safe_num(r.get("storage_cost_share"))
    forecast_units = _safe_num(r.get("forecast_12w_units"))
    lead_time = _safe_num(r.get("lead_time_days"))
    days_of_cover = _safe_num(r.get("days_of_cover"))
    risk_flags = 1.0 if str(r.get("policy_risk","")).lower() in ("critical","high") else 0.0

    # Normalize each to 0..1 band (heuristics)
    # margin: target 30%-60%
    n_margin = _norm_unit(gross_margin, 0.10, 0.60, invert=False)
    n_star   = _norm_unit(avg_star, 3.5, 5.0, invert=False)
    n_rr     = _norm_unit(return_rate, 0.0, 0.10, invert=False)  # higher worse
    n_bbgap  = _norm_unit(buybox_gap, -0.05, 0.10, invert=False) # positive gap helpful
    n_kw     = _norm_unit(keyword_rank if keyword_rank>0 else 50, 50, 1, invert=True)  # lower rank better
    n_lift   = _norm_unit(promo_lift, 0.0, 0.30, invert=False)
    n_roas   = _norm_unit(roas, 0.8, 3.0, invert=False)
    n_store  = _norm_unit(storage_cost_share, 0.0, 0.15, invert=False)
    n_fcst   = _norm_unit(forecast_units, 0.0, 2000.0, invert=False)
    n_lead   = _norm_unit(lead_time if lead_time>0 else 60, 60, 1, invert=True)  # shorter better
    n_cover  = _norm_unit(days_of_cover if days_of_cover>0 else 60, 7, 60, invert=False) # too high -> worse
    n_risk   = 1.0 if risk_flags > 0 else 0.0

    # Weighted sum
    parts = {
        "gross_margin": n_margin * w["gross_margin"],
        "avg_star": n_star * w["avg_star"],
        "return_rate": n_rr * w["return_rate"],
        "buybox_gap": n_bbgap * w["buybox_gap"],
        "keyword_rank": n_kw * w["keyword_rank"],
        "promo_lift": n_lift * w["promo_lift"],
        "roas": n_roas * w["roas"],
        "storage_cost_share": n_store * w["storage_cost_share"],
        "forecast_units": n_fcst * w["forecast_units"],
        "lead_time": n_lead * w["lead_time"],
        "days_of_cover": n_cover * w["days_of_cover"],
        "risk_flags": n_risk * w["risk_flags"],
    }
    raw = sum(parts.values())
    # Normalize score to 0..100 using sigmoid-ish mapping to emphasize mid-high
    score = 100.0 / (1.0 + math.exp(-raw/5.0))
    return score, parts
