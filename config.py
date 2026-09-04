import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', f'sqlite:///{os.path.join(BASE_DIR, "data", "poputka.db")}')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flags for mocking external services
MOCK_2GIS = os.getenv('MOCK_2GIS', 'true').lower() == 'true'
TWOGIS_API_KEY = os.getenv('TWOGIS_API_KEY', '')

MOCK_EMAIL = os.getenv('MOCK_EMAIL', 'true').lower() == 'true'
RUSENDER_API_KEY = os.getenv('RUSENDER_API_KEY', '')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Mock coordinates for well-known points in Yekaterinburg
MOCK_COORDS = {
    'уралмаш': (56.8927, 60.6074),
    'урфу': (56.8389, 60.5905),
    'урфу главное здание': (56.8389, 60.5905),
    'площадь 1905 года': (56.8380, 60.5967),
    'втузгородок': (56.8345, 60.6204),
    'втузгородок 1': (56.8345, 60.6204),
    'втузгородок 2': (56.8340, 60.6220),
    'академический': (56.8252, 60.5769),
    'академгородок': (56.8252, 60.5769),
    'жк солнечный': (56.8135, 60.5735),
    'жк академический': (56.8252, 60.5769),
    'центр': (56.8380, 60.5967),
    'вокзал': (56.8413, 60.5834),
    'екб': (56.8380, 60.5967),
    'екатеринбург': (56.8380, 60.5967),
    'метро ботаническая': (56.8185, 60.6050),
    'метро уральская': (56.8385, 60.5930),
    'метро геологическая': (56.8310, 60.5940),
    'метро чкаловская': (56.8240, 60.6120),
}
