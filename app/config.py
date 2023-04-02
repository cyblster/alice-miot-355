import os
from dotenv import load_dotenv


load_dotenv()


APP_HOST = os.getenv('APP_HOST')
APP_PORT = int(os.getenv('APP_PORT', default=5000))
APP_SSL_CRT = os.getenv('APP_SSL_CRT')
APP_SSL_KEY = os.getenv('APP_SSL_KEY')
APP_ID = os.getenv('APP_ID')
APP_SECRET = os.getenv('APP_SECRET')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', default=5432))
DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PW')
DB_NAME = os.getenv('DB_NAME')
DB_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

FAN_HOST = os.getenv('FAN_HOST')
FAN_TOKEN = os.getenv('FAN_TOKEN')

VACUUM_HOST = os.getenv('VACUUM_HOST')
VACUUM_TOKEN = os.getenv('VACUUM_TOKEN')

TV_HOST = os.getenv('TV_HOST')
TV_MAC = os.getenv('TV_MAC')
