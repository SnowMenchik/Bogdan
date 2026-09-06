import random
from config import MOCK_COORDS, MOCK_2GIS, TWOGIS_API_KEY

def search_address(query):
    """Search for addresses/places. Returns list of {address, lat, lon}."""
    if not query or len(query) < 1:
        # Return ALL known addresses (for datalist population)
        return [
            {'address': key.title(), 'lat': coords[0], 'lon': coords[1]}
            for key, coords in MOCK_COORDS.items()
        ]
    query_lower = query.lower()
    results = []
    for key, coords in MOCK_COORDS.items():
        if query_lower in key:
            results.append({
                'address': key.title(),
                'lat': coords[0],
                'lon': coords[1],
            })
    return results

def validate_address(address):
    """Check if address exists in our database. Returns (is_valid, lat, lon)."""
    if not address:
        return False, None, None
    addr_lower = address.lower().strip()
    # Exact match or substring match in MOCK_COORDS
    for key, coords in MOCK_COORDS.items():
        if addr_lower == key or key in addr_lower or addr_lower in key:
            return True, coords[0], coords[1]
    # Not found in known addresses
    return False, None, None

def get_coordinates(address):
    if MOCK_2GIS or not TWOGIS_API_KEY:
        return _mock_geocode(address)
    return _mock_geocode(address)

def _mock_geocode(address):
    addr_lower = address.lower()
    for key, coords in MOCK_COORDS.items():
        if key in addr_lower:
            return coords
    # Return None if address not found — strict validation
    return None

def get_traffic_multiplier(departure_datetime, start_point='', end_point=''):
    if MOCK_2GIS or not TWOGIS_API_KEY:
        hour = departure_datetime.hour
        dow = departure_datetime.weekday()
        if dow >= 5:
            return 1.0
        elif 7 <= hour <= 9 or 17 <= hour <= 19:
            return random.uniform(1.2, 1.5)
        elif 10 <= hour <= 15:
            return random.uniform(0.8, 1.0)
        else:
            return 1.0
    return 1.0

def get_route_info(start, end):
    start_coords = get_coordinates(start)
    end_coords = get_coordinates(end)
    from geopy.distance import geodesic
    distance = geodesic(start_coords, end_coords).km
    time_hours = distance / 40
    return {'distance_km': round(distance, 2), 'time_minutes': round(time_hours * 60, 0), 'traffic_multiplier': 1.0}
