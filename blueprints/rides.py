from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Ride, RideRequest, Route
from services.route_service import create_route, create_ride_from_route
from services.request_service import create_request
from services.bonus_service import check_bonus
from services.matching_service import find_matches_for_request
from services.auth_service import create_notification

rides_bp = Blueprint('rides', __name__)


@rides_bp.route('/create_route', methods=['GET', 'POST'])
@login_required
def create_route_page():
    if request.method == 'POST':
        start_point = request.form.get('start_point', '').strip()
        end_point = request.form.get('end_point', '').strip()
        departure_time = request.form.get('departure_time', '').strip()
        days_of_week = request.form.getlist('days')
        available_seats = int(request.form.get('available_seats', 1))
        zero_stress_mode = request.form.get('zero_stress_mode') == 'on'
        ride_date = request.form.get('ride_date', '').strip()  # optional

        # QoL prefs override
        music_pref = request.form.get('music_pref', current_user.music_pref)
        talk_pref = request.form.get('talk_pref', current_user.talk_pref)
        ac_pref = request.form.get('ac_pref', current_user.ac_pref)
        smoking = request.form.get('smoking') == 'on'

        route = create_route(
            current_user.id, start_point, end_point, departure_time,
            ','.join(days_of_week) if days_of_week else '',
            available_seats, zero_stress_mode, music_pref, talk_pref, ac_pref, smoking
        )

        # Optionally create a Ride for a specific date
        if ride_date:
            from datetime import datetime
            dt = None
            try:
                dt = datetime.strptime(f'{ride_date} {departure_time}', '%Y-%m-%d %H:%M')
            except ValueError:
                try:
                    dt = datetime.strptime(f'{ride_date} {departure_time}', '%Y-%m-%d %H:%M')
                except ValueError:
                    flash('Неверный формат даты.', 'error')
            if dt:
                ride = create_ride_from_route(route, dt)
                flash(f'Маршрут и поездка созданы на {ride_date}!', 'success')
                return redirect(url_for('rides.ride_detail', ride_id=ride.id))

        flash('Маршрут создан!', 'success')
        return redirect(url_for('rides.ride_list'))

    return render_template('create_route.html')


@rides_bp.route('/create_request', methods=['GET', 'POST'])
@login_required
def create_request_page():
    if request.method == 'POST':
        start_point = request.form.get('start_point', '').strip()
        end_point = request.form.get('end_point', '').strip()
        desired_time = request.form.get('desired_time', '').strip()
        flexibility = int(request.form.get('flexibility', 15))
        seats = int(request.form.get('seats', 1))

        music_pref = request.form.get('music_pref', current_user.music_pref)
        talk_pref = request.form.get('talk_pref', current_user.talk_pref)
        ac_pref = request.form.get('ac_pref', current_user.ac_pref)
        smoking = request.form.get('smoking') == 'on'

        from datetime import datetime
        dt = None
        try:
            dt = datetime.strptime(desired_time, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Неверный формат времени.', 'error')

        if dt:
            req = create_request(
                current_user.id, start_point, end_point, dt,
                flexibility, seats, music_pref, talk_pref, ac_pref, smoking
            )
            flash('Запрос создан! Ищем попутчиков...', 'success')
            return redirect(url_for('rides.ride_list'))
        return redirect(url_for('rides.create_request_page'))

    return render_template('create_request.html')


@rides_bp.route('/list')
@login_required
def ride_list():
    my_rides = Ride.query.filter_by(driver_id=current_user.id).order_by(Ride.departure_datetime.desc()).all()
    my_requests = RideRequest.query.filter_by(passenger_id=current_user.id).order_by(RideRequest.created_at.desc()).all()
    return render_template('ride_list.html', my_rides=my_rides, my_requests=my_requests)


@rides_bp.route('/<int:ride_id>')
@login_required
def ride_detail(ride_id):
    ride = db.session.get(Ride, ride_id)
    if not ride:
        flash('Поездка не найдена.', 'error')
        return redirect(url_for('rides.ride_list'))

    matches = []
    if ride.driver_id == current_user.id:
        # Show pending matches for this ride's requests
        pass
    elif ride.driver_id != current_user.id:
        # Passenger view
        pass

    return render_template('ride_detail.html', ride=ride, matches=matches)


@rides_bp.route('/<int:ride_id>/cancel', methods=['POST'])
@login_required
def cancel_ride(ride_id):
    ride = db.session.get(Ride, ride_id)
    if not ride or (ride.driver_id != current_user.id and not any(
        m.request.passenger_id == current_user.id for m in ride.matches
    )):
        flash('У вас нет прав для отмены.', 'error')
        return redirect(url_for('rides.ride_list'))

    ride.status = 'cancelled'
    for m in ride.matches:
        if m.status == 'accepted':
            m.status = 'rejected'
            create_notification(m.request.passenger_id, f'Поездка {ride.start_point} -> {ride.end_point} отменена водителем.')

    if ride.driver_id == current_user.id:
        create_notification(current_user.id, 'Вы отменили свою поездку.')
    db.session.commit()
    flash('Поездка отменена.', 'warning')
    return redirect(url_for('rides.ride_list'))


@rides_bp.route('/<int:ride_id>/complete', methods=['POST'])
@login_required
def complete_ride(ride_id):
    ride = db.session.get(Ride, ride_id)
    if not ride or ride.driver_id != current_user.id:
        flash('Только водитель может завершить поездку.', 'error')
        return redirect(url_for('rides.ride_list'))

    ride.status = 'completed'
    for m in ride.matches:
        if m.status == 'accepted':
            m.status = 'completed'
            create_notification(m.request.passenger_id, f'Поездка {ride.start_point} -> {ride.end_point} завершена. Оцените водителя!')
    create_notification(current_user.id, 'Поездка завершена. Оцените пассажиров!')
    db.session.commit()
    flash('Поездка завершена!', 'success')
    return redirect(url_for('rides.ride_list'))


@rides_bp.route('/parse_text', methods=['POST'])
@login_required
def parse_text():
    from ml.llm_parser import parse_text_request
    text = request.form.get('text', '')
    result = parse_text_request(text)
    if result:
        return render_template('create_request.html', parsed=result)
    else:
        flash('Не удалось распознать запрос. Попробуйте ещё раз.', 'error')
        return redirect(url_for('rides.create_request_page'))
