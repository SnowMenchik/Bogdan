from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Ride, Match, Rating
from services.rating_service import create_rating

ratings_bp = Blueprint('ratings', __name__)


@ratings_bp.route('/rate/<int:ride_id>/<int:to_user_id>', methods=['GET', 'POST'])
@login_required
def rate_user(ride_id, to_user_id):
    ride = db.session.get(Ride, ride_id)
    if not ride or ride.status != 'completed':
        flash('Поездка не завершена.', 'error')
        return redirect(url_for('rides.ride_list'))

    # Check if already rated
    existing = Rating.query.filter_by(from_user_id=current_user.id, to_user_id=to_user_id, ride_id=ride_id).first()
    if existing:
        flash('Вы уже оценили этого пользователя.', 'warning')
        return redirect(url_for('rides.ride_detail', ride_id=ride_id))

    if request.method == 'POST':
        if current_user.id == ride.driver_id:
            # Driver rating passenger
            rating = create_rating(
                current_user.id, to_user_id, ride_id, 'driver_to_passenger',
                politeness=int(request.form.get('politeness', 3)),
                punctuality_passenger=int(request.form.get('punctuality_passenger', 3)),
                tidiness=int(request.form.get('tidiness', 3)),
                comment=request.form.get('comment', '').strip()
            )
        else:
            # Passenger rating driver
            rating = create_rating(
                current_user.id, to_user_id, ride_id, 'passenger_to_driver',
                cleanliness=int(request.form.get('cleanliness', 3)),
                driving_style=int(request.form.get('driving_style', 3)),
                comfort=int(request.form.get('comfort', 3)),
                communication=int(request.form.get('communication', 3)),
                punctuality=int(request.form.get('punctuality', 3)),
                comment=request.form.get('comment', '').strip()
            )
        flash('Оценка сохранена!', 'success')
        return redirect(url_for('rides.ride_detail', ride_id=ride_id))

    to_user = db.session.get(Rating, 1)  # placeholder, get actual user
    from models import User
    to_user = db.session.get(User, to_user_id)

    return render_template('rate_user.html', ride=ride, to_user=to_user, is_driver=current_user.id == ride.driver_id)
