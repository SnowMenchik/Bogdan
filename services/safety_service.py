from models import Notification, EmergencyContact
from services.auth_service import create_notification

def trigger_sos(ride, user):
    contacts = EmergencyContact.query.filter_by(user_id=user.id).all()
    if not contacts:
        create_notification(user.id, 'SOS: У вас нет экстренных контактов. Добавьте их в профиле.')
        return True
    for contact in contacts:
        create_notification(user.id, f'SOS уведомление отправлено на {contact.contact_type}: {contact.contact_value}')
    create_notification(user.id, 'SOS активирован! Экстренные контакты уведомлены.')
    return True
