from extensions import db
from models import RideRequest
from integrations.twogis import get_coordinates


def create_request(passenger_id, start_point, end_point, desired_departure_time,
                   flexibility_minutes=15, seats_needed=1,
                   music_pref='neutral', talk_pref='neutral', ac_pref='no_matter', smoking=False):
    """Создать запрос пассажира."""
    start_coords = get_coordinates(start_point)
    end_coords = get_coordinates(end_point)

    req = RideRequest(
        passenger_id=passenger_id,
        start_point=start_point,
        end_point=end_point,
        start_lat=start_coords[0],
        start_lon=start_coords[1],
        end_lat=end_coords[0],
        end_lon=end_coords[1],
        desired_departure_time=desired_departure_time,
        flexibility_minutes=flexibility_minutes,
        seats_needed=seats_needed,
        music_pref=music_pref,
        talk_pref=talk_pref,
        ac_pref=ac_pref,
        smoking=smoking,
    )
    db.session.add(req)
    db.session.commit()
    return req
