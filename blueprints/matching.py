from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import RideRequest, Ride, Match
from services.matching_service import find_matches_for_request
from services.auth_service import create_notification

matching_bp = Blueprint('matching', __name__)

@matching_bp.route('/find/<int:request_id>')
@login_required
def find_matches(request_id):
    req = db.session.get(RideRequest, request_id)
    if not req or req.passenger_id != current_user.id:
        flash('Запрос не найден.', 'error')
        return redirect(url_for('rides.ride_list'))
    matches = find_matches_for_request(req)
    return render_template('matching_results.html', request=req, matches=matches)

@matching_bp.route('/accept/<int:ride_id>/<int:request_id>', methods=['POST'])
@login_required
def accept_match(ride_id, request_id):
    ride = db.session.get(Ride, ride_id)
    req = db.session.get(RideRequest, request_id)
    if not ride or not req or req.passenger_id != current_user.id:
        flash('Поездка или запрос не найдены.', 'error')
        return redirect(url_for('rides.ride_list'))

    # Create the match and accept it
    match = Match(request_id=req.id, ride_id=ride.id, score=0.5, compatibility_score=0.5, status='accepted')
    db.session.add(match)

    ride.seats_available -= req.seats_needed
    req.status = 'matched'
    create_notification(ride.driver_id, f'Пассажир {current_user.full_name} принял вашу поездку {ride.start_point} -> {ride.end_point}!')
    db.session.commit()
    flash('Предложение принято!', 'success')
    return redirect(url_for('rides.ride_detail', ride_id=ride.id))

@matching_bp.route('/reject/<int:ride_id>/<int:request_id>', methods=['POST'])
@login_required
def reject_match(ride_id, request_id):
    ride = db.session.get(Ride, ride_id)
    req = db.session.get(RideRequest, request_id)
    if not ride or not req or req.passenger_id != current_user.id:
        flash('Поездка или запрос не найдены.', 'error')
        return redirect(url_for('rides.ride_list'))

    match = Match(request_id=req.id, ride_id=ride.id, score=0, compatibility_score=0, status='rejected')
    db.session.add(match)
    db.session.commit()
    flash('Предложение отклонено.', 'info')
    return redirect(url_for('matching.find_matches', request_id=req.id))
