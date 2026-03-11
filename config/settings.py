import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5434'),
    'dbname': os.getenv('DB_NAME', 'metro_bh'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASS', 'Seinfra2025'), 
    'schema': os.getenv('DB_SCHEMA', 'migracao')
}