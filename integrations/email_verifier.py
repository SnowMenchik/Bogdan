import random
from config import MOCK_EMAIL, RUSENDER_API_KEY

def send_verification_code(email, user_name):
    code = str(random.randint(1000, 9999))
    if MOCK_EMAIL or not RUSENDER_API_KEY:
        return code
    return code

def send_notification_email(email, subject, body):
    if MOCK_EMAIL or not RUSENDER_API_KEY:
        return True
    return True
