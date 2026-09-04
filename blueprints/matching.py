from flask import Blueprint, render_template, request, redirect, url_for, flash
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


@matching_bp.route('/accept/<int:match_id>', methods=['POST'])
@login_required
def accept_match(match_id):
    match = db.session.get(Match, match_id)
    if not match or match.request.passenger_id != current_user.id:
        flash('Матч не найден.', 'error')
        return redirect(url_for('rides.ride_list'))

    match.status = 'accepted'
    ride = db.session.get(Ride, match.ride_id)
    ride.seats_available -= match.request.seats_needed
    match.request.status = 'matched'

    create_notification(ride.driver_id, f'Пассажир {current_user.full_name} принял вашу поездку {ride.start_point} -> {ride.end_point}!')
    db.session.commit()
    flash('Предложение принято!', 'success')
    return redirect(url_for('rides.ride_detail', ride_id=ride.id))


@matching_bp.route('/reject/<int:match_id>', methods=['POST'])
@login_required
def reject_match(match_id):
    match = db.session.get(Match, match_id)
    if not match or match.request.passenger_id != current_user.id:
        flash('Матч не найден.', 'error')
        return redirect(url_for('rides.ride_list'))

    match.status = 'rejected'
    db.session.commit()
    flash('Предложение отклонено.', 'info')
    return redirect(url_for('matching.find_matches', request_id=match.request_id))
