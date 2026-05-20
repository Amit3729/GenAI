import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is missing")
    return psycopg2.connect(db_url)

def execute_query(sql_query: str) -> list[dict]:
    """Executes a SQL query and returns the results as a list of dictionaries."""
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql_query)
                if cursor.description is not None:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                return []
    except Exception as e:
        raise e
