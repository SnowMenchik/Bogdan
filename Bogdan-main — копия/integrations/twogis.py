import random
from config import MOCK_COORDS, MOCK_2GIS, TWOGIS_API_KEY


def get_coordinates(address):
    """Получить координаты по адресу (мок или реальный 2GIS)."""
    if MOCK_2GIS or not TWOGIS_API_KEY:
        return _mock_geocode(address)

    # Real 2GIS API would go here
    return _mock_geocode(address)


def _mock_geocode(address):
    """Мок-геокодирование по словарю."""
    addr_lower = address.lower()
    for key, coords in MOCK_COORDS.items():
        if key in addr_lower:
            return coords

    # Generate random coords near Yekaterinburg center
    lat = 56.8380 + random.uniform(-0.05, 0.05)
    lon = 60.5967 + random.uniform(-0.05, 0.05)
    return (round(lat, 6), round(lon, 6))


def get_traffic_multiplier(departure_datetime, start_point='', end_point=''):
    """Получить множитель пробок (мок или реальный 2GIS)."""
    if MOCK_2GIS or not TWOGIS_API_KEY:
        hour = departure_datetime.hour
        dow = departure_datetime.weekday()

        if dow >= 5:  # Weekend
            return 1.0
        elif 7 <= hour <= 9 or 17 <= hour <= 19:  # Peak
            return random.uniform(1.2, 1.5)
        elif 10 <= hour <= 15:  # Off-peak
            return random.uniform(0.8, 1.0)
        else:
            return 1.0

    return 1.0


def get_route_info(start, end):
    """Получить информацию о маршруте (расстояние, время)."""
    start_coords = get_coordinates(start)
    end_coords = get_coordinates(end)

    from geopy.distance import geodesic
    distance = geodesic(start_coords, end_coords).km
    # Approximate time: 40 km/h avg in city
    time_hours = distance / 40

    return {
        'distance_km': round(distance, 2),
        'time_minutes': round(time_hours * 60, 0),
        'traffic_multiplier': 1.0,
    }
