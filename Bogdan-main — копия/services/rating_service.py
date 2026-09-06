from extensions import db
from models import Rating


def create_rating(from_user_id, to_user_id, ride_id, rating_type,
                  cleanliness=None, driving_style=None, comfort=None, communication=None, punctuality=None,
                  politeness=None, punctuality_passenger=None, tidiness=None, comment=None):
    """Создать оценку."""
    rating = Rating(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        ride_id=ride_id,
        rating_type=rating_type,
        cleanliness=cleanliness,
        driving_style=driving_style,
        comfort=comfort,
        communication=communication,
        punctuality=punctuality,
        politeness=politeness,
        punctuality_passenger=punctuality_passenger,
        tidiness=tidiness,
        comment=comment,
    )
    db.session.add(rating)
    db.session.commit()
    return rating


def get_user_ratings(user_id):
    """Получить средние оценки пользователя."""
    ratings = Rating.query.filter_by(to_user_id=user_id).all()
    if not ratings:
        return None

    result = {}
    if any(r.rating_type == 'passenger_to_driver' for r in ratings):
        driver_ratings = [r for r in ratings if r.rating_type == 'passenger_to_driver']
        result['as_driver'] = {
            'cleanliness': round(sum(r.cleanliness or 3 for r in driver_ratings) / len(driver_ratings), 1),
            'driving_style': round(sum(r.driving_style or 3 for r in driver_ratings) / len(driver_ratings), 1),
            'comfort': round(sum(r.comfort or 3 for r in driver_ratings) / len(driver_ratings), 1),
            'communication': round(sum(r.communication or 3 for r in driver_ratings) / len(driver_ratings), 1),
            'punctuality': round(sum(r.punctuality or 3 for r in driver_ratings) / len(driver_ratings), 1),
        }

    if any(r.rating_type == 'driver_to_passenger' for r in ratings):
        passenger_ratings = [r for r in ratings if r.rating_type == 'driver_to_passenger']
        result['as_passenger'] = {
            'politeness': round(sum(r.politeness or 3 for r in passenger_ratings) / len(passenger_ratings), 1),
            'punctuality_passenger': round(sum(r.punctuality_passenger or 3 for r in passenger_ratings) / len(passenger_ratings), 1),
            'tidiness': round(sum(r.tidiness or 3 for r in passenger_ratings) / len(passenger_ratings), 1),
        }

    return result
