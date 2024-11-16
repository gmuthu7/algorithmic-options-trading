from datetime import datetime, timedelta

from setting import DAILY_TTL_HOUR


def set_expiry_of_model_to_daily(model):
    now = datetime.now()
    next = now.replace(hour=DAILY_TTL_HOUR, minute=0, second=0, microsecond=0)
    if now >= next:
        next += timedelta(days=1)
    ttl = int((next - now).total_seconds())
    model.expire(ttl)
