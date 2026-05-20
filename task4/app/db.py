from sqlalchemy import create_engine
from config import settings

engine = create_engine(settings.DATABASE_URL)

def get_connection():
    return engine.connect()