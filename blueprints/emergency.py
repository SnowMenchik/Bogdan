from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Ride, EmergencyContact
from services.safety_service import trigger_sos

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/sos/<int:ride_id>', methods=['POST'])
@login_required
def sos(ride_id):
    ride = db.session.get(Ride, ride_id)
    if not ride:
        flash('Поездка не найдена.', 'error')
        return redirect(url_for('dashboard'))
    result = trigger_sos(ride, current_user)
    if result:
        flash('SOS сигнал отправлен экстренным контактам!', 'danger')
    else:
        flash('Не удалось отправить SOS.', 'error')
    return redirect(url_for('rides.ride_detail', ride_id=ride_id))

@emergency_bp.route('/add_contact', methods=['POST'])
@login_required
def add_contact():
    contact_type = request.form.get('contact_type', 'phone')
    contact_value = request.form.get('contact_value', '').strip()
    if contact_value:
        contact = EmergencyContact(user_id=current_user.id, contact_type=contact_type, contact_value=contact_value)
        db.session.add(contact)
        db.session.commit()
        flash('Экстренный контакт добавлен.', 'success')
    return redirect(url_for('users.profile'))
