from extensions import db
from models import Ride, Match, User, Rating
from integrations.twogis import get_coordinates
from services.preferences_service import calculate_compatibility
from geopy.distance import geodesic


def find_matches_for_request(request, max_results=5):
    """Найти подходящие поездки для запроса пассажира."""
    candidates = Ride.query.filter(
        Ride.status == 'planned',
        Ride.seats_available >= request.seats_needed
    ).all()

    scored = []
    for ride in candidates:
        # Time window check
        time_diff_minutes = abs((ride.departure_datetime - request.desired_departure_time).total_seconds()) / 60
        max_flex = request.flexibility_minutes
        if time_diff_minutes > max_flex:
            continue

        # Distance check
        max_dist = 0.5 if ride.zero_stress_mode else 1.5  # km
        if ride.start_lat and request.start_lat:
            dist = geodesic(
                (request.start_lat, request.start_lon),
                (ride.start_lat, ride.start_lon)
            ).km
            if dist > max_dist:
                continue
        else:
            dist = 1.0  # default

        # Scores
        time_score = max(0, 1 - time_diff_minutes / max_flex)
        distance_score = max(0, 1 - dist / max_dist)
        compat_score = calculate_compatibility(ride, request)

        # Driver rating
        driver = db.session.get(User, ride.driver_id)
        ratings = Rating.query.filter_by(to_user_id=driver.id).all()
        if ratings:
            avg_rating = sum(
                (r.cleanliness or r.politeness or 3) +
                (r.driving_style or r.punctuality_passenger or 3) +
                (r.comfort or r.tidiness or 3) +
                (r.communication or 3) +
                (r.punctuality or 3)
                for r in ratings
            ) / (5 * len(ratings))
            rating_score = avg_rating / 5.0
        else:
            rating_score = 0.5  # neutral for new drivers

        total_score = (
            0.35 * time_score +
            0.2 * distance_score +
            0.3 * compat_score +
            0.15 * rating_score
        )

        scored.append({
            'match': None,  # will be created on accept
            'ride': ride,
            'driver': driver,
            'score': round(total_score, 2),
            'compatibility': round(compat_score * 100),
            'time_score': round(time_score, 2),
            'distance_score': round(distance_score, 2),
            'price': ride.price_per_seat,
            'explanation': _generate_explanation(driver, ride, request),
        })

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:max_results]


def _generate_explanation(driver, ride, request):
    """Генерация объяснения совместимости."""
    parts = []
    if driver.music_pref == request.music_pref and driver.music_pref != 'neutral':
        parts.append(f'оба предпочитают музыку: {driver.music_pref}')
    if driver.talk_pref == request.talk_pref and driver.talk_pref != 'neutral':
        parts.append('совпадение по разговорчивости')
    if driver.smoking == request.smoking:
        parts.append('совпадение по курению')
    if not parts:
        parts.append('хорошая совместимость по маршруту и времени')
    return 'Высокая совместимость: ' + ', '.join(parts).capitalize()
