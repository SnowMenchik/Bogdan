import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, Route, Ride, RideRequest, BonusRule, Rating, Notification, Payment

app = create_app()
with app.app_context():
    if User.query.first():
        print('Database already has data. Skipping seed.')
        sys.exit(0)
    print('Seeding database...')
    u1 = User(full_name='Иванов Иван', email='ivanov@stud.urfu.ru', role='both', is_verified=True)
    u1.set_password('password123'); u1.music_pref = 'love'; u1.talk_pref = 'talk'
    u1.car_model = 'Kia Rio'; u1.car_color = 'Белый'
    u2 = User(full_name='Петрова Анна', email='petrova@stud.urfu.ru', role='passenger', is_verified=True)
    u2.set_password('password123'); u2.music_pref = 'no'; u2.talk_pref = 'silence'
    u3 = User(full_name='Сидоров Алексей', email='sidorov@stud.urfu.ru', role='driver', is_verified=True)
    u3.set_password('password123'); u3.car_model = 'Hyundai Solaris'; u3.car_color = 'Чёрный'
    u4 = User(full_name='Козлова Мария', email='kozlova@stud.urfu.ru', role='both', is_verified=True)
    u4.set_password('password123')
    u5 = User(full_name='Новиков Дмитрий', email='novikov@stud.urfu.ru', role='passenger', is_verified=True)
    u5.set_password('password123')
    db.session.add_all([u1, u2, u3, u4, u5]); db.session.commit()
    print(f'Created {User.query.count()} users')
    tomorrow = datetime.now() + timedelta(days=1)
    r1 = Route(driver_id=u1.id, start_point='Уралмаш', end_point='УрФУ',
        start_lat=56.8927, start_lon=60.6074, end_lat=56.8389, end_lon=60.5905,
        departure_time='08:30', days_of_week='0,1,2,3,4', available_seats=3)
    db.session.add(r1); db.session.commit()
    ride1 = Ride(driver_id=u1.id, route_id=r1.id, start_point='Уралмаш', end_point='УрФУ',
        start_lat=56.8927, start_lon=60.6074, end_lat=56.8389, end_lon=60.5905,
        departure_datetime=tomorrow.replace(hour=8, minute=30, second=0, microsecond=0),
        seats_total=3, seats_available=2, price_per_seat=85.0, status='planned')
    ride2 = Ride(driver_id=u3.id, start_point='Академический', end_point='УрФУ',
        start_lat=56.8252, start_lon=60.5769, end_lat=56.8389, end_lon=60.5905,
        departure_datetime=tomorrow.replace(hour=9, minute=0, second=0, microsecond=0),
        seats_total=2, seats_available=2, price_per_seat=65.0, status='planned')
    yesterday = datetime.now() - timedelta(days=1)
    ride3 = Ride(driver_id=u1.id, start_point='Втузгородок', end_point='УрФУ',
        start_lat=56.8345, start_lon=60.6204, end_lat=56.8389, end_lon=60.5905,
        departure_datetime=yesterday.replace(hour=10, minute=0, second=0, microsecond=0),
        seats_total=2, seats_available=1, price_per_seat=55.0, status='completed')
    db.session.add_all([ride1, ride2, ride3]); db.session.commit()
    print(f'Created {Ride.query.count()} rides')
    req1 = RideRequest(passenger_id=u2.id, start_point='Уралмаш', end_point='УрФУ',
        start_lat=56.8927, start_lon=60.6074, end_lat=56.8389, end_lon=60.5905,
        desired_departure_time=tomorrow.replace(hour=8, minute=45, second=0, microsecond=0),
        flexibility_minutes=20, seats_needed=1, status='open')
    req2 = RideRequest(passenger_id=u5.id, start_point='Площадь 1905 года', end_point='Втузгородок',
        desired_departure_time=tomorrow.replace(hour=12, minute=0, second=0, microsecond=0),
        flexibility_minutes=15, seats_needed=1, status='open')
    db.session.add_all([req1, req2]); db.session.commit()
    print(f'Created {RideRequest.query.count()} requests')
    bonus1 = BonusRule(day_of_week=None, start_hour=10, end_hour=15, bonus_percent=0.15)
    bonus2 = BonusRule(day_of_week=5, start_hour=0, end_hour=23, bonus_percent=0.10)
    bonus3 = BonusRule(day_of_week=6, start_hour=0, end_hour=23, bonus_percent=0.10)
    db.session.add_all([bonus1, bonus2, bonus3]); db.session.commit()
    print(f'Created {BonusRule.query.count()} bonus rules')
    rat1 = Rating(from_user_id=u2.id, to_user_id=u1.id, ride_id=ride3.id,
        rating_type='passenger_to_driver', cleanliness=5, driving_style=4, comfort=5,
        communication=4, punctuality=5, comment='Отличный водитель!')
    rat2 = Rating(from_user_id=u1.id, to_user_id=u2.id, ride_id=ride3.id,
        rating_type='driver_to_passenger', politeness=5, punctuality_passenger=5,
        tidiness=4, comment='Вежливый пассажир')
    db.session.add_all([rat1, rat2]); db.session.commit()
    n1 = Notification(user_id=u1.id, message='Добро пожаловать в Попутка ИИ!')
    n2 = Notification(user_id=u2.id, message='Ваш запрос создан.')
    db.session.add_all([n1, n2]); db.session.commit()
    p1 = Payment(user_id=u2.id, ride_id=ride3.id, amount=55.0, status='mock_paid')
    db.session.add(p1); db.session.commit()
    print('Seed complete!')
    print('Demo users: ivanov@stud.urfu.ru / password123, petrova@stud.urfu.ru / password123, etc.')
