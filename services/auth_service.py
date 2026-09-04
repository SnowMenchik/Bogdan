import re
import random
from flask import flash, redirect, url_for, session
from extensions import db
from models import User, Notification
from integrations.email_verifier import send_verification_code


URFU_EMAIL_PATTERN = re.compile(r'^[\w.+-]+@stud\.urfu\.ru$')


def register_user(full_name, email, password, role='passenger'):
    """Регистрация нового пользователя с проверкой email."""
    if not URFU_EMAIL_PATTERN.match(email):
        flash('Email должен заканчиваться на @stud.urfu.ru', 'error')
        return None

    if User.query.filter_by(email=email).first():
        flash('Пользователь с таким email уже существует.', 'error')
        return None

    user = User(full_name=full_name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Send verification
    code = send_verification_code(email, user.full_name)
    session['verification_user_id'] = user.id
    session['verification_code'] = code
    flash(f'Код подтверждения отправлен на {email}', 'info')
    return user


def verify_user(code):
    """Проверка кода верификации."""
    expected = session.get('verification_code')
    user_id = session.get('verification_user_id')

    if not expected or not user_id:
        flash('Сессия верификации истекла. Зарегистрируйтесь заново.', 'error')
        return False

    if str(code).strip() == str(expected).strip():
        user = db.session.get(User, user_id)
        if user:
            user.is_verified = True
            db.session.commit()
            flash('Email успешно подтверждён!', 'success')
            session.pop('verification_code', None)
            session.pop('verification_user_id', None)
            return True
        else:
            flash('Пользователь не найден.', 'error')
            return False
    else:
        flash('Неверный код подтверждения.', 'error')
        return False


def login_user(email, password):
    """Вход пользователя."""
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Пользователь не найден.', 'error')
        return None
    if not user.check_password(password):
        flash('Неверный пароль.', 'error')
        return None
    if not user.is_verified:
        flash('Email не подтверждён. Сначала подтвердите регистрацию.', 'warning')
        session['verification_user_id'] = user.id
        return None
    return user


def create_notification(user_id, message):
    """Создать уведомление для пользователя."""
    notif = Notification(user_id=user_id, message=message)
    db.session.add(notif)
    db.session.commit()
    return notif
