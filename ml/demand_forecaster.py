from datetime import datetime

def forecast_demand(date=None):
    if date is None:
        date = datetime.now()
    dow = date.weekday()
    hour = date.hour
    if dow >= 5:
        return 'medium'
    elif 7 <= hour <= 9 or 17 <= hour <= 19:
        return 'high'
    elif 10 <= hour <= 15:
        return 'low'
    else:
        return 'medium'

def get_demand_multiplier(date=None):
    level = forecast_demand(date)
    return {'low': 0.8, 'medium': 1.0, 'high': 1.3}.get(level, 1.0)
