from extensions import db
from models import RideRequest
from integrations.twogis import get_coordinates, validate_address

def create_request(passenger_id, start_point, end_point, desired_departure_time,
                   flexibility_minutes=15, seats_needed=1,
                   music_pref='neutral', talk_pref='neutral', ac_pref='no_matter', smoking=False):
    start_valid, start_lat, start_lon = validate_address(start_point)
    if not start_valid:
        coords = get_coordinates(start_point)
        start_lat, start_lon = coords if coords else (None, None)

    end_valid, end_lat, end_lon = validate_address(end_point)
    if not end_valid:
        coords = get_coordinates(end_point)
        end_lat, end_lon = coords if coords else (None, None)

    req = RideRequest(passenger_id=passenger_id, start_point=start_point, end_point=end_point,
        start_lat=start_lat, start_lon=start_lon,
        end_lat=end_lat, end_lon=end_lon,
        desired_departure_time=desired_departure_time, flexibility_minutes=flexibility_minutes,
        seats_needed=seats_needed, music_pref=music_pref, talk_pref=talk_pref,
        ac_pref=ac_pref, smoking=smoking)
    db.session.add(req)
    db.session.commit()
    return req
