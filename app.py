import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from extensions import db, login_manager, bcrypt

from blueprints.auth import auth_bp
from blueprints.users import users_bp
from blueprints.rides import rides_bp
from blueprints.matching import matching_bp
from blueprints.ratings import ratings_bp
from blueprints.emergency import emergency_bp


def create_app():
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(rides_bp, url_prefix='/rides')
    app.register_blueprint(matching_bp, url_prefix='/matching')
    app.register_blueprint(ratings_bp, url_prefix='/ratings')
    app.register_blueprint(emergency_bp, url_prefix='/emergency')

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))

    # Main routes
    @app.route('/')
    def index():
        from models import Notification
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return render_template('index.html', unread_count=unread_count)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        from models import Ride, RideRequest, Notification
        my_rides = Ride.query.filter_by(driver_id=current_user.id).order_by(Ride.departure_datetime.desc()).limit(5).all()
        my_requests = RideRequest.query.filter_by(passenger_id=current_user.id).order_by(RideRequest.created_at.desc()).limit(5).all()
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return render_template('dashboard.html', my_rides=my_rides, my_requests=my_requests, unread_count=unread_count)

    @app.route('/notifications')
    @login_required
    def notifications():
        from models import Notification
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
        return render_template('notifications.html', notifications=notifications)

    with app.app_context():
        os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
