# src/database/verify_database.py (updated)

import sqlite3
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.database_setup import DatabaseManager
from sqlalchemy import text


def verify_database():
    """Verify database structure and connections."""
    db = DatabaseManager()

    try:
        # Test direct SQLite connection
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Database tables: {[t[0] for t in tables]}")

        # Check social_posts table structure
        cursor.execute("PRAGMA table_info(social_posts);")
        columns = cursor.fetchall()
        print("\nSocial Posts table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

        conn.close()

        # Test SQLAlchemy connection
        engine = db.create_sqlalchemy_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("\nSQLAlchemy connection: SUCCESS")

            # Test insertion
            test_insert = text("""
            INSERT INTO social_posts 
            (platform, post_url, username, followers, caption, likes, comments, shares, created_at)
            VALUES (:platform, :post_url, :username, :followers, :caption, :likes, :comments, :shares, :created_at)
            """)

            test_data = {
                'platform': 'test',
                'post_url': 'test_url',
                'username': 'test_user',
                'followers': 100,
                'caption': 'test caption',
                'likes': 10,
                'comments': 2,
                'shares': 1,
                'created_at': '2025-04-21 23:30:00'
            }

            conn.execute(test_insert, test_data)
            conn.commit()
            print("Test insertion: SUCCESS")

            # Clean up test data
            conn.execute(text("DELETE FROM social_posts WHERE platform = 'test'"))
            conn.commit()
            print("Test data cleanup: SUCCESS")

    except Exception as e:
        print(f"Error verifying database: {e}")


if __name__ == "__main__":
    verify_database()