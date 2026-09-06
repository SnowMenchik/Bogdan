from extensions import db
from models import BonusRule

def check_bonus(departure_datetime):
    dow = departure_datetime.weekday()
    hour = departure_datetime.hour
    rules = BonusRule.query.all()
    for rule in rules:
        if (rule.day_of_week is None or rule.day_of_week == dow) and rule.start_hour <= hour < rule.end_hour:
            return rule
    return None

def get_bonus_percent(departure_datetime):
    rule = check_bonus(departure_datetime)
    return rule.bonus_percent if rule else 0.0
