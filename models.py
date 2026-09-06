from datetime import datetime
from flask_login import UserMixin
from extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='passenger')
    is_verified = db.Column(db.Boolean, default=False)

    music_pref = db.Column(db.String(20), default='neutral')
    talk_pref = db.Column(db.String(20), default='neutral')
    ac_pref = db.Column(db.String(20), default='no_matter')
    smoking = db.Column(db.Boolean, default=False)

    max_daily_hours = db.Column(db.Float, default=6.0)
    break_interval_min = db.Column(db.Integer, default=60)

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
    contact_type = db.Column(db.String(20), nullable=False)
    contact_value = db.Column(db.String(100), nullable=False)


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
    departure_time = db.Column(db.String(10), nullable=False)
    days_of_week = db.Column(db.String(20), nullable=True)
    available_seats = db.Column(db.Integer, nullable=False, default=1)
    zero_stress_mode = db.Column(db.Boolean, default=False)
    music_pref = db.Column(db.String(20), default='neutral')
    talk_pref = db.Column(db.String(20), default='neutral')
    ac_pref = db.Column(db.String(20), default='no_matter')
    smoking = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


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
    status = db.Column(db.String(20), default='planned')
    bonus_applied = db.Column(db.Boolean, default=False)
    zero_stress_mode = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    matches = db.relationship('Match', backref='ride', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='ride', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='ride', lazy=True, cascade='all, delete-orphan')


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
    music_pref = db.Column(db.String(20), default='neutral')
    talk_pref = db.Column(db.String(20), default='neutral')
    ac_pref = db.Column(db.String(20), default='no_matter')
    smoking = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    matches = db.relationship('Match', backref='request', lazy=True, cascade='all, delete-orphan')


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('ride_requests.id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    compatibility_score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='proposed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=False)
    rating_type = db.Column(db.String(30), nullable=False)
    cleanliness = db.Column(db.Integer, nullable=True)
    driving_style = db.Column(db.Integer, nullable=True)
    comfort = db.Column(db.Integer, nullable=True)
    communication = db.Column(db.Integer, nullable=True)
    punctuality = db.Column(db.Integer, nullable=True)
    politeness = db.Column(db.Integer, nullable=True)
    punctuality_passenger = db.Column(db.Integer, nullable=True)
    tidiness = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BonusRule(db.Model):
    __tablename__ = 'bonus_rules'
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=True)
    start_hour = db.Column(db.Integer, nullable=False)
    end_hour = db.Column(db.Integer, nullable=False)
    bonus_percent = db.Column(db.Float, nullable=False, default=0.15)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
