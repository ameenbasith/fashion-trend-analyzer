# src/database/find_databases.py

import os
import sqlite3


def find_all_databases(root_dir):
    """Find all fashion_trends.db files in the project."""
    db_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == 'fashion_trends.db':
                full_path = os.path.join(dirpath, filename)
                db_files.append(full_path)

    return db_files


def check_database_tables(db_path):
    """Check which tables exist in a database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        return [t[0] for t in tables]
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    # Get project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Find all database files
    db_files = find_all_databases(project_root)

    print(f"Found {len(db_files)} database files:")
    for i, db_path in enumerate(db_files, 1):
        print(f"\n{i}. {db_path}")
        tables = check_database_tables(db_path)
        print(f"   Tables: {tables}")