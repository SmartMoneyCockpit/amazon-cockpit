
from __future__ import annotations
def get_templates():
    return [
        {"name":"ACoS > 25% (7d)","metric":"acos","operator":">","threshold":0.25,"lookback_days":7},
        {"name":"TACoS > 30% (7d)","metric":"tacos","operator":">","threshold":0.30,"lookback_days":7},
        {"name":"Refund Rate > 2% (14d)","metric":"refund_rate","operator":">","threshold":0.02,"lookback_days":14},
        {"name":"GMV crosses below 1000 (7d)","metric":"gmv","operator":"crosses_below","threshold":1000.0,"lookback_days":7},
        {"name":"GMV crosses above 5000 (7d)","metric":"gmv","operator":"crosses_above","threshold":5000.0,"lookback_days":7},
    ]
