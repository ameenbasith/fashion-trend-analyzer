# src/database/debug_connection.py

import os
import sys
import sqlite3
from sqlalchemy import create_engine, text

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.database_setup import DatabaseManager


def debug_connections():
    print(f"Project root: {project_root}")

    # Check database path from DatabaseManager
    db = DatabaseManager()
    print(f"DatabaseManager db_path: {db.db_path}")
    print(f"Database file exists: {os.path.exists(db.db_path)}")

    # Try direct SQLite connection
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"SQLite tables: {[t[0] for t in tables]}")
        conn.close()
    except Exception as e:
        print(f"SQLite error: {e}")

    # Try SQLAlchemy connection
    try:
        engine = create_engine(f'sqlite:///{db.db_path}')
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = result.fetchall()
            print(f"SQLAlchemy tables: {[t[0] for t in tables]}")
    except Exception as e:
        print(f"SQLAlchemy error: {e}")

    # Try a test INSERT with SQLAlchemy
    try:
        engine = create_engine(f'sqlite:///{db.db_path}')
        with engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO social_posts 
                (platform, post_url, username, followers, caption, likes, comments, shares, created_at)
                VALUES ('test', 'test_url', 'test_user', 100, 'test', 10, 5, 1, '2025-04-21 23:30:00')
            """))
            conn.commit()
            print("Test insert successful")

            # Clean up
            conn.execute(text("DELETE FROM social_posts WHERE platform = 'test'"))
            conn.commit()
    except Exception as e:
        print(f"Test insert error: {e}")


if __name__ == "__main__":
    debug_connections()