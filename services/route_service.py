from extensions import db
from models import Route, Ride
from integrations.twogis import get_coordinates, validate_address
from services.pricing_service import calculate_price
from datetime import datetime

def create_route(driver_id, start_point, end_point, departure_time, days_of_week,
                 available_seats, zero_stress_mode, music_pref, talk_pref, ac_pref, smoking):
    # Try validate first, fallback to geocode
    start_valid, start_lat, start_lon = validate_address(start_point)
    if not start_valid:
        coords = get_coordinates(start_point)
        start_lat, start_lon = coords if coords else (None, None)

    end_valid, end_lat, end_lon = validate_address(end_point)
    if not end_valid:
        coords = get_coordinates(end_point)
        end_lat, end_lon = coords if coords else (None, None)

    route = Route(driver_id=driver_id, start_point=start_point, end_point=end_point,
        start_lat=start_lat, start_lon=start_lon,
        end_lat=end_lat, end_lon=end_lon,
        departure_time=departure_time, days_of_week=days_of_week,
        available_seats=available_seats, zero_stress_mode=zero_stress_mode,
        music_pref=music_pref, talk_pref=talk_pref, ac_pref=ac_pref, smoking=smoking)
    db.session.add(route)
    db.session.commit()
    return route

def create_ride_from_route(route, departure_datetime):
    seats_total = route.available_seats
    price = calculate_price(route.start_point, route.end_point, seats_total, departure_datetime,
        route.start_lat, route.start_lon, route.end_lat, route.end_lon)
    ride = Ride(driver_id=route.driver_id, route_id=route.id,
        start_point=route.start_point, end_point=route.end_point,
        start_lat=route.start_lat, start_lon=route.start_lon,
        end_lat=route.end_lat, end_lon=route.end_lon,
        departure_datetime=departure_datetime, seats_total=seats_total,
        seats_available=seats_total, price_per_seat=price,
        bonus_applied=False, zero_stress_mode=route.zero_stress_mode)
    db.session.add(ride)
    db.session.commit()
    return ride
