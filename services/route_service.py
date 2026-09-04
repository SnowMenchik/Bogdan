from extensions import db
from models import Route, Ride
from integrations.twogis import get_coordinates
from services.pricing_service import calculate_price
from services.bonus_service import check_bonus
from datetime import datetime


def create_route(driver_id, start_point, end_point, departure_time, days_of_week,
                 available_seats, zero_stress_mode, music_pref, talk_pref, ac_pref, smoking):
    """Создать маршрут водителя."""
    start_coords = get_coordinates(start_point)
    end_coords = get_coordinates(end_point)

    route = Route(
        driver_id=driver_id,
        start_point=start_point,
        end_point=end_point,
        start_lat=start_coords[0],
        start_lon=start_coords[1],
        end_lat=end_coords[0],
        end_lon=end_coords[1],
        departure_time=departure_time,
        days_of_week=days_of_week,
        available_seats=available_seats,
        zero_stress_mode=zero_stress_mode,
        music_pref=music_pref,
        talk_pref=talk_pref,
        ac_pref=ac_pref,
        smoking=smoking,
    )
    db.session.add(route)
    db.session.commit()
    return route


def create_ride_from_route(route, departure_datetime):
    """Создать конкретную поездку из маршрута."""
    seats_total = route.available_seats
    price = calculate_price(
        route.start_point, route.end_point,
        seats_total, departure_datetime,
        route.start_lat, route.start_lon, route.end_lat, route.end_lon
    )

    bonus = check_bonus(departure_datetime)

    ride = Ride(
        driver_id=route.driver_id,
        route_id=route.id,
        start_point=route.start_point,
        end_point=route.end_point,
        start_lat=route.start_lat,
        start_lon=route.start_lon,
        end_lat=route.end_lat,
        end_lon=route.end_lon,
        departure_datetime=departure_datetime,
        seats_total=seats_total,
        seats_available=seats_total,
        price_per_seat=price,
        bonus_applied=bonus is not None,
        zero_stress_mode=route.zero_stress_mode,
    )
    db.session.add(ride)
    db.session.commit()
    return ride


def check_driver_qwl(driver_id, date):
    """Проверить QWL ограничения водителя."""
    from datetime import datetime, timedelta
    day_start = datetime.combine(date, datetime.min.time())
    day_end = day_start + timedelta(days=1)

    rides = Ride.query.filter(
        Ride.driver_id == driver_id,
        Ride.departure_datetime >= day_start,
        Ride.departure_datetime < day_end,
        Ride.status.in_(['planned', 'active'])
    ).all()

    if not rides:
        return None, 0.0

    total_hours = 0
    for ride in rides:
        # Approximate duration based on distance
        from geopy.distance import geodesic
        if ride.start_lat and ride.end_lat:
            dist = geodesic((ride.start_lat, ride.start_lon), (ride.end_lat, ride.end_lon)).km
            total_hours += dist / 40  # avg 40 km/h in city
        else:
            total_hours += 0.5

    user = db.session.get(type(rides[0].driver), driver_id)
    max_hours = user.max_daily_hours if user else 6.0
    return total_hours, max_hours
