from extensions import db
from models import Notification

def create_notification(user_id, message):
    notif = Notification(user_id=user_id, message=message)
    db.session.add(notif)
    db.session.commit()
    return notif

def get_unread_count(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()

def mark_all_read(user_id):
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
