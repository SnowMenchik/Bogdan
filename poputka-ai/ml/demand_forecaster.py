from datetime import datetime


def forecast_demand(date=None):
    """
    Заглушка прогноза спроса.
    Возвращает примерный уровень спроса для дня (low, medium, high).
    """
    if date is None:
        date = datetime.now()

    dow = date.weekday()  # 0=Monday
    hour = date.hour

    # Simple mock logic
    if dow >= 5:  # Weekend
        return 'medium'
    elif 7 <= hour <= 9 or 17 <= hour <= 19:  # Peak hours
        return 'high'
    elif 10 <= hour <= 15:  # Off-peak
        return 'low'
    else:
        return 'medium'


def get_demand_multiplier(date=None):
    """Получить множитель спроса для ценообразования."""
    level = forecast_demand(date)
    multipliers = {
        'low': 0.8,
        'medium': 1.0,
        'high': 1.3,
    }
    return multipliers.get(level, 1.0)
