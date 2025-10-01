import pandas as pd
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PPCAction:
    level: str      # "Campaign" | "Keyword"
    target: str     # campaign name or keyword
    action: str     # "Raise Budget", "Cut Budget", "Raise Bid", "Lower Bid", "Add Negative", "Pause"
    reason: str
    amount: Optional[float] = None   # suggested delta (budget or bid)
    campaign: Optional[str] = None
    match_type: Optional[str] = None

def guardrails(df: pd.DataFrame, acos_target: float = 30.0, min_conv: int = 5) -> List[PPCAction]:
    """
    Campaign-level rules:
    - If ACoS% <= target and Orders >= min_conv -> Raise Budget +10%
    - If ACoS% > target*1.3 and Orders < min_conv -> Cut Budget -15%
    """
    actions: List[PPCAction] = []
    if df is None or df.empty:
        return actions
    # Expect columns: Campaign, Orders, ACoS%, Spend
    grp = df.groupby("Campaign", as_index=False).agg({"Orders":"sum", "ACoS%":"mean", "Spend":"sum"})
    for _, r in grp.iterrows():
        if r["ACoS%"] <= acos_target and r["Orders"] >= min_conv:
            amt = float(r["Spend"] * 0.10)  # suggest +10% of recent spend as budget bump
            actions.append(PPCAction("Campaign", r["Campaign"], "Raise Budget",
                                     f"ACoS {r['ACoS%']:.1f}% ≤ target and Orders {int(r['Orders'])}≥{min_conv}", amount=round(amt,2)))
        elif r["ACoS%"] > acos_target*1.3 and r["Orders"] < min_conv:
            amt = float(r["Spend"] * 0.15)
            actions.append(PPCAction("Campaign", r["Campaign"], "Cut Budget",
                                     f"ACoS {r['ACoS%']:.1f}% ≫ target and low Orders {int(r['Orders'])}<{min_conv}", amount=round(amt,2)))
    return actions

def bid_rules(kw_df: pd.DataFrame, acos_target: float = 30.0, min_clicks: int = 20) -> List[PPCAction]:
    """
    Keyword-level rules (expects columns: Keyword, MatchType, Campaign, Clicks, Orders, ACoS%, ROAS):
    - If Clicks >= min and Orders = 0 and ACoS% > 0 -> Lower Bid -15% (waste clicks)
    - If ACoS% <= target and Orders >= 3 -> Raise Bid +10%
    - If ACoS% > target*1.5 and Orders <= 1 -> Lower Bid -20% or Pause if Clicks >= 50
    """
    actions: List[PPCAction] = []
    if kw_df is None or kw_df.empty:
        return actions
    for _, r in kw_df.iterrows():
        clicks = float(r.get("Clicks", 0))
        orders = float(r.get("Orders", 0))
        acos = float(r.get("ACoS%", 0))
        kw = str(r.get("Keyword", "(unknown)"))
        mt = str(r.get("MatchType", ""))
        camp = str(r.get("Campaign", ""))
        if clicks >= min_clicks and orders == 0 and acos > 0:
            actions.append(PPCAction("Keyword", kw, "Lower Bid", f"Waste clicks: {int(clicks)} clicks, 0 orders", amount=0.15, campaign=camp, match_type=mt))
        elif acos <= acos_target and orders >= 3:
            actions.append(PPCAction("Keyword", kw, "Raise Bid", f"Profitable: ACoS {acos:.1f}% ≤ target, {int(orders)} orders", amount=0.10, campaign=camp, match_type=mt))
        elif acos > acos_target*1.5 and orders <= 1:
            if clicks >= 50:
                actions.append(PPCAction("Keyword", kw, "Pause", f"High ACoS {acos:.1f}% with {int(clicks)} clicks and {int(orders)} orders", campaign=camp, match_type=mt))
            else:
                actions.append(PPCAction("Keyword", kw, "Lower Bid", f"High ACoS {acos:.1f}% with low orders {int(orders)}", amount=0.20, campaign=camp, match_type=mt))
    return actions

def negatives(df: pd.DataFrame, ctr_floor: float = 0.10, min_impr: int = 2000) -> List[PPCAction]:
    """
    Negative keyword candidates (expects columns: Keyword, Campaign, Impressions, Clicks):
    - If Impressions >= min_impr and CTR < ctr_floor and Orders == 0 -> Add Negative (search term mining proxy)
    """
    actions: List[PPCAction] = []
    if df is None or df.empty:
        return actions
    df = df.copy()
    if "Impressions" in df.columns and "Clicks" in df.columns:
        df["CTR"] = (df["Clicks"] / df["Impressions"]).fillna(0.0)
    else:
        df["CTR"] = 0.0
    for _, r in df.iterrows():
        impr = float(r.get("Impressions", 0))
        ctr = float(r.get("CTR", 0.0))
        orders = float(r.get("Orders", 0))
        if impr >= min_impr and ctr < ctr_floor and orders == 0:
            kw = str(r.get("Keyword", "(unknown)"))
            camp = str(r.get("Campaign",""))
            actions.append(PPCAction("Keyword", kw, "Add Negative", f"Low CTR {ctr:.2%} on {int(impr)} impr, 0 orders", campaign=camp))
    return actions

def actions_to_df(items: List[PPCAction]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=["level","target","action","reason","amount","campaign","match_type"])
    return pd.DataFrame([a.__dict__ for a in items])
