from extensions import db
from models import BonusRule


def check_bonus(departure_datetime):
    """Проверить, попадает ли время в бонусный интервал."""
    dow = departure_datetime.weekday()  # 0=Monday
    hour = departure_datetime.hour

    rules = BonusRule.query.all()
    for rule in rules:
        if (rule.day_of_week is None or rule.day_of_week == dow) and \
           rule.start_hour <= hour < rule.end_hour:
            return rule
    return None


def get_bonus_percent(departure_datetime):
    """Получить процент бонуса для времени."""
    rule = check_bonus(departure_datetime)
    return rule.bonus_percent if rule else 0.0
