from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import register_user, verify_user, login_user as auth_login
from config import ALLOW_ANY_EMAIL

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'passenger')
        user = register_user(full_name, email, password, role)
        if user:
            return redirect(url_for('auth.verify'))
        return redirect(url_for('auth.register'))
    return render_template('register.html', allow_any_email=ALLOW_ANY_EMAIL)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = auth_login(email, password)
        if user:
            login_user(user)
            flash(f'Добро пожаловать, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        from models import User
        existing = User.query.filter_by(email=email).first()
        if existing and not existing.is_verified:
            session['verification_user_id'] = existing.id
            flash('Email не подтверждён. Введите код.', 'warning')
            return redirect(url_for('auth.verify'))
        return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        if verify_user(code):
            return redirect(url_for('auth.login'))
        return redirect(url_for('auth.verify'))
    mock_code = session.get('verification_code')
    return render_template('verify.html', mock_code=mock_code)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))
