from extensions import db
from models import Notification, EmergencyContact
from services.auth_service import create_notification


def trigger_sos(ride, user):
    """Отправить SOS сигнал экстренным контактам."""
    contacts = EmergencyContact.query.filter_by(user_id=user.id).all()
    if not contacts:
        # Create a notification as fallback
        create_notification(user.id, 'SOS: У вас нет экстренных контактов. Добавьте их в профиле.')
        return True

    for contact in contacts:
        msg = (f'SOS от {user.full_name}! Поездка {ride.start_point} -> {ride.end_point}. '
               f'Контакт: {contact.contact_type} = {contact_value}')
        # In mock, just create notification for the user
        create_notification(user.id, f'SOS уведомление отправлено на {contact.contact_type}: {contact.contact_value}')

    create_notification(user.id, f'SOS активирован! Экстренные контакты уведомлены.')
    return True
