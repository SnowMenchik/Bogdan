from geopy.distance import geodesic
from integrations.twogis import get_traffic_multiplier


def calculate_price(start_point, end_point, seats_total, departure_datetime,
                    start_lat=None, start_lon=None, end_lat=None, end_lon=None):
    """Рассчитать цену за место в поездке."""
    # Distance
    if start_lat and end_lat:
        distance_km = geodesic((start_lat, start_lon), (end_lat, end_lon)).km
    else:
        distance_km = 10  # default

    base_price = 50 + (distance_km * 15)
    traffic_mult = get_traffic_multiplier(departure_datetime, start_point, end_point)
    total = base_price * traffic_mult

    price_per_seat = max(total / max(seats_total, 1), 30)  # minimum 30 rub
    return round(price_per_seat, 2)


def estimate_taxi_price(distance_km):
    """Оценить стоимость такси для сравнения."""
    return round(distance_km * 50, 2)
