"""
Lifecycle Engine
Simulates the biological 42-day lifespan of red blood cells,
daily donation inflow, emergency transfusion outflow, and dynamic stock changes.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

def calculate_daily_inventory(records: List[Dict[str, Any]], target_day_offset: int = 0) -> Dict[str, Any]:
    """
    Computes available inventory and flow rates on a given day offset (0 = today).
    Filters units where:
      - collectionDate <= targetDate
      - expiryDate > targetDate
      - status == 'safe'
    """
    target_date = datetime.utcnow() + timedelta(days=target_day_offset)
    target_day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    target_day_end = target_day_start + timedelta(days=1)

    stock_by_bg = {bg: 0 for bg in BLOOD_GROUPS}
    collected_today = 0
    transfused_today = 0
    expired_today = 0

    for r in records:
        coll = datetime.fromisoformat(r['collectionDate'])
        exp = datetime.fromisoformat(r['expiryDate'])
        status = r.get('status', 'safe')
        units = r.get('units', 1)
        bg = r.get('bloodGroup')

        # Check if collected on this target day
        if target_day_start <= coll < target_day_end:
            collected_today += units

        # Check if expired on this target day
        if target_day_start <= exp < target_day_end:
            expired_today += units

        # Check if currently valid and safe on target date
        if coll <= target_date < exp:
            if status == 'safe':
                if bg in stock_by_bg:
                    stock_by_bg[bg] += units
            elif status == 'used' and (target_day_start <= coll < target_day_end):
                transfused_today += units

    total_safe_units = sum(stock_by_bg.values())

    return {
        "targetDate": target_date.strftime("%Y-%m-%d"),
        "dayOffset": target_day_offset,
        "totalSafeUnits": total_safe_units,
        "stockByBloodGroup": stock_by_bg,
        "collectedToday": collected_today,
        "transfusedToday": transfused_today,
        "expiredToday": expired_today
    }
