# config.py
from urllib.parse import quote_plus

DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_NAME = "postgres"

RAW_PASSWORD = "1"
DB_PASS = quote_plus(RAW_PASSWORD)

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

TARGET_SCHEMA = "RPLM"
TARGET_TABLE = "_tekhnologicheskie_protses"