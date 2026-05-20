import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://text2sql:text2sql_pass@localhost:5434/text2sql_db")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

settings = Settings()