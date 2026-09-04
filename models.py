from datetime import datetime
from flask_login import UserMixin
from extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='passenger')  # 'driver', 'passenger', 'both'
    is_verified = db.Column(db.Boolean, default=False)

    # QoL preferences
    music_pref = db.Column(db.String(20), default='neutral')  # 'love', 'no', 'neutral'
    talk_pref = db.Column(db.String(20), default='neutral')  # 'talk', 'silence', 'neutral'
    ac_pref = db.Column(db.String(20), default='no_matter')  # 'must', 'no_matter'
    smoking = db.Column(db.Boolean, default=False)

    # QWL constraints
    max_daily_hours = db.Column(db.Float, default=6.0)
    break_interval_min = db.Column(db.Integer, default=60)

    # Vehicle info (optional)
    car_model = db.Column(db.String(50), nullable=True)
    car_color = db.Column(db.String(30), nullable=True)

    emergency_contacts = db.relationship('EmergencyContact', backref='user', lazy=True, cascade='all, delete-orphan')
    routes = db.relationship('Route', backref='driver', lazy=True, cascade='all, delete-orphan')
    rides = db.relationship('Ride', backref='driver', lazy=True, cascade='all, delete-orphan', foreign_keys='Ride.driver_id')
    requests = db.relationship('RideRequest', backref='passenger', lazy=True, cascade='all, delete-orphan')
    ratings_given = db.relationship('Rating', backref='from_user', lazy=True, foreign_keys='Rating.from_user_id', cascade='all, delete-orphan')
    ratings_received = db.relationship('Rating', backref='to_user', lazy=True, foreign_keys='Rating.to_user_id', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.full_name}>'


class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_type = db.Column(db.String(20), nullable=False)  # 'phone', 'email', 'telegram'
    contact_value = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<EmergencyContact {self.contact_value}>'


class Route(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_point = db.Column(db.String(200), nullable=False)
    end_point = db.Column(db.String(200), nullable=False)
    start_lat = db.Column(db.Float, nullable=True)
    start_lon = db.Column(db.Float, nullable=True)
    end_lat = db.Column(db.Float, nullable=True)
    end_lon = db.Column(db.Float, nullable=True)
    departure_time = db.Column(db.String(10), nullable=False)  # "08:30"
    days_of_week = db.Column(db.String(20), nullable=True)  # "1,2,3,4,5"
    available_seats = db.Column(db.Integer, nullable=False, default=1)
    zero_stress_mode = db.Column(db.Boolean, default=False)

    # Preferences override
    music_pref = db.Column(db.String(20), default='neutral')
    talk_pref = db.Column(db.String(20), default='neutral')
    ac_pref = db.Column(db.String(20), default='no_matter')
    smoking = db.Column(db.Boolean, default=False)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rides = db.relationship('Ride', backref='route', lazy=True)

    def __repr__(self):
        return f'<Route {self.start_point} -> {self.end_point}>'


class Ride(db.Model):
    __tablename__ = 'rides'

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=True)
    start_point = db.Column(db.String(200), nullable=False)
    end_point = db.Column(db.String(200), nullable=False)
    start_lat = db.Column(db.Float, nullable=True)
    start_lon = db.Column(db.Float, nullable=True)
    end_lat = db.Column(db.Float, nullable=True)
    end_lon = db.Column(db.Float, nullable=True)
    departure_datetime = db.Column(db.DateTime, nullable=False)
    seats_total = db.Column(db.Integer, nullable=False, default=1)
    seats_available = db.Column(db.Integer, nullable=False, default=1)
    price_per_seat = db.Column(db.Float, nullable=False, default=50.0)
    status = db.Column(db.String(20), default='planned')  # 'planned', 'active', 'completed', 'cancelled'
    bonus_applied = db.Column(db.Boolean, default=False)
    zero_stress_mode = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    matches = db.relationship('Match', backref='ride', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='ride', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='ride', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Ride {self.start_point} -> {self.end_point} {self.departure_datetime}>'


class RideRequest(db.Model):
    __tablename__ = 'ride_requests'

    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_point = db.Column(db.String(200), nullable=False)
    end_point = db.Column(db.String(200), nullable=False)
    start_lat = db.Column(db.Float, nullable=True)
    start_lon = db.Column(db.Float, nullable=True)
    end_lat = db.Column(db.Float, nullable=True)
    end_lon = db.Column(db.Float, nullable=True)
    desired_departure_time = db.Column(db.DateTime, nullable=False)
    flexibility_minutes = db.Column(db.Integer, default=15)
    seats_needed = db.Column(db.Integer, default=1)

    # Preferences JSON-like
    music_pref = db.Column(db.String(20), default='neutral')
    talk_pref = db.Column(db.String(20), default='neutral')
    ac_pref = db.Column(db.String(20), default='no_matter')
    smoking = db.Column(db.Boolean, default=False)

    status = db.Column(db.String(20), default='open')  # 'open', 'matched', 'closed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    matches = db.relationship('Match', backref='request', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<RideRequest {self.start_point} -> {self.end_point}>'


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('ride_requests.id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    compatibility_score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='proposed')  # 'proposed', 'accepted', 'rejected', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Match score={self.score}>'


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=False)
    rating_type = db.Column(db.String(30), nullable=False)  # 'driver_to_passenger', 'passenger_to_driver'

    # Passenger rating of driver criteria
    cleanliness = db.Column(db.Integer, nullable=True)
    driving_style = db.Column(db.Integer, nullable=True)
    comfort = db.Column(db.Integer, nullable=True)
    communication = db.Column(db.Integer, nullable=True)
    punctuality = db.Column(db.Integer, nullable=True)

    # Driver rating of passenger criteria
    politeness = db.Column(db.Integer, nullable=True)
    punctuality_passenger = db.Column(db.Integer, nullable=True)
    tidiness = db.Column(db.Integer, nullable=True)

    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Rating from={self.from_user_id} to={self.to_user_id}>'


class BonusRule(db.Model):
    __tablename__ = 'bonus_rules'

    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=True)  # 0-6, NULL = every day
    start_hour = db.Column(db.Integer, nullable=False)
    end_hour = db.Column(db.Integer, nullable=False)
    bonus_percent = db.Column(db.Float, nullable=False, default=0.15)

    def __repr__(self):
        return f'<BonusRule {self.start_hour}:00-{self.end_hour}:00 {self.bonus_percent*100}%>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.message[:30]}>'


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'mock_paid'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.amount} {self.status}>'
