from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, EmergencyContact

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.car_model = request.form.get('car_model', '').strip() or None
        current_user.car_color = request.form.get('car_color', '').strip() or None
        current_user.role = request.form.get('role', current_user.role)
        contact_values = request.form.getlist('emergency_contact')
        contact_types = request.form.getlist('emergency_type')
        EmergencyContact.query.filter_by(user_id=current_user.id).delete()
        for ctype, cval in zip(contact_types, contact_values):
            if cval.strip():
                contact = EmergencyContact(user_id=current_user.id, contact_type=ctype, contact_value=cval.strip())
                db.session.add(contact)
        db.session.commit()
        flash('Профиль обновлён.', 'success')
        return redirect(url_for('users.profile'))
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', contacts=contacts)

@users_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    if request.method == 'POST':
        current_user.music_pref = request.form.get('music_pref', 'neutral')
        current_user.talk_pref = request.form.get('talk_pref', 'neutral')
        current_user.ac_pref = request.form.get('ac_pref', 'no_matter')
        current_user.smoking = request.form.get('smoking') == 'on'
        current_user.max_daily_hours = float(request.form.get('max_daily_hours', 6.0))
        current_user.break_interval_min = int(request.form.get('break_interval_min', 60))
        db.session.commit()
        flash('Предпочтения обновлены.', 'success')
        return redirect(url_for('users.preferences'))
    return render_template('preferences.html')
