from extensions import db
from models import Rating

def create_rating(from_user_id, to_user_id, ride_id, rating_type,
                  cleanliness=None, driving_style=None, comfort=None, communication=None, punctuality=None,
                  politeness=None, punctuality_passenger=None, tidiness=None, comment=None):
    rating = Rating(from_user_id=from_user_id, to_user_id=to_user_id, ride_id=ride_id,
        rating_type=rating_type, cleanliness=cleanliness, driving_style=driving_style,
        comfort=comfort, communication=communication, punctuality=punctuality,
        politeness=politeness, punctuality_passenger=punctuality_passenger,
        tidiness=tidiness, comment=comment)
    db.session.add(rating)
    db.session.commit()
    return rating
