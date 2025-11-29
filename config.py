# config.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

def get_db_connection():
    """Establishes and returns a database connection."""
    if not DB_URL:
        raise ValueError("DATABASE_URL not found in environment variables.")
    try:
        # NOTE: psycopg2.connect() is called here
        conn = psycopg2.connect(DB_URL)
        return conn
    except psycopg2.Error as e:
        # Re-raise the exception after printing the error
        print(f"Error connecting to PostgreSQL: {e}")
        raise