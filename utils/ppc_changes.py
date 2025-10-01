"""
Translate optimizer actions into a Bulk Changes CSV compatible layout
you can adapt for Amazon Ads Console / bulk operations.

We produce three sheets (as separate CSVs):
1) campaigns.csv  -> budget changes
2) keywords.csv   -> bid changes & pauses
3) negatives.csv  -> negatives for search terms/keywords

Note: Exact bulk schema varies by region/version. This keeps a generic,
human-editable format that maps cleanly to Ads bulk upload columns.
"""
import pandas as pd

def actions_split(actions_df: pd.DataFrame):
    if actions_df is None or actions_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Campaign budget changes
    camp = actions_df[actions_df["level"]=="Campaign"].copy()
    camp = camp[["target","action","amount","reason"]].rename(columns={
        "target":"CampaignName",
        "amount":"BudgetDelta"
    })
    # Normalize sign
    def _delta(row):
        if row["action"]=="Raise Budget":
            return abs(float(row.get("BudgetDelta",0)))
        elif row["action"]=="Cut Budget":
            return -abs(float(row.get("BudgetDelta",0)))
        return 0.0
    if not camp.empty:
        camp["BudgetDelta"] = camp.apply(_delta, axis=1)
        camp["Action"] = camp["action"]
        camp = camp[["CampaignName","Action","BudgetDelta","reason"]]

    # Keyword bid changes / pause
    kw = actions_df[actions_df["level"]=="Keyword"].copy()
    kw["BidDelta"] = 0.0
    kw.loc[kw["action"]=="Raise Bid","BidDelta"]  =  0.10  # 10% up
    kw.loc[kw["action"]=="Lower Bid","BidDelta"]  = -0.15  # 15% down (or 20% if set)
    kw = kw.rename(columns={
        "target":"Keyword",
        "campaign":"CampaignName",
        "match_type":"MatchType"
    })
    kw = kw[["CampaignName","Keyword","MatchType","action","BidDelta","reason"]]
    kw["Action"] = kw["action"]
    kw = kw[["CampaignName","Keyword","MatchType","Action","BidDelta","reason"]]

    # Negatives
    neg = actions_df[actions_df["action"]=="Add Negative"].copy()
    neg = neg.rename(columns={
        "target":"Keyword",
        "campaign":"CampaignName",
        "match_type":"MatchType"
    })
    if "MatchType" not in neg.columns:
        neg["MatchType"] = "Negative Phrase"
    neg["NegativeType"] = neg["MatchType"].apply(lambda x: "Negative Exact" if "Exact" in str(x) else "Negative Phrase")
    neg = neg[["CampaignName","Keyword","NegativeType","reason"]]

    return camp.reset_index(drop=True), kw.reset_index(drop=True), neg.reset_index(drop=True)

def to_bytes_csv(df: pd.DataFrame) -> bytes:
    return (df if df is not None else pd.DataFrame()).to_csv(index=False).encode("utf-8")

def build_changes_log(actions_df: pd.DataFrame, actor: str = "cockpit") -> pd.DataFrame:
    """Flat log for archiving: timestamp, actor, and the original action fields."""
    import datetime as dt
    log = actions_df.copy() if actions_df is not None else pd.DataFrame()
    if log.empty:
        return pd.DataFrame(columns=["timestamp","actor","level","target","action","amount","campaign","match_type","reason"])
    log.insert(0, "timestamp", dt.datetime.utcnow().isoformat(timespec="seconds")+"Z")
    log.insert(1, "actor", actor)
    return log
