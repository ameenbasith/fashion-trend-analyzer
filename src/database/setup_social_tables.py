# src/database/setup_social_tables.py

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.database_setup import DatabaseManager
from src.analysis.social_trend_analyzer import create_social_schema


def setup_social_tables():
    """Create social media tables in the database."""
    db = DatabaseManager()
    schema_sql = create_social_schema()

    try:
        conn = db.create_connection()
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        print("Social media tables created successfully")

        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Current database tables:")
        for table in tables:
            print(f"  - {table[0]}")

    except Exception as e:
        print(f"Error creating social media tables: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    setup_social_tables()