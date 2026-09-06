import random
from config import MOCK_EMAIL, RUSENDER_API_KEY


def send_verification_code(email, user_name):
    """Отправить код подтверждения на email (мок или RuSender)."""
    code = str(random.randint(1000, 9999))

    if MOCK_EMAIL or not RUSENDER_API_KEY:
        # Mock: just return code, it will be shown in UI
        return code

    # Real RuSender API would go here
    # import requests
    # response = requests.post('https://api.rusender.com/send', ...)
    # if response.status_code == 200:
    #     return code

    return code


def send_notification_email(email, subject, body):
    """Отправить уведомление на email (мок)."""
    if MOCK_EMAIL or not RUSENDER_API_KEY:
        return True

    # Real implementation would use RuSender
    return True
