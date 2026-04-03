import psycopg2
from config import DB_CONFIG


def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn


def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100),
            phone VARCHAR(20) NOT NULL UNIQUE
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Table 'phonebook' is ready.")
