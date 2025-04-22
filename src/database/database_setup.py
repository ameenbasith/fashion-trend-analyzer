# src/database/database_setup.py

import sqlite3
import os
from sqlalchemy import create_engine
import pandas as pd


class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Use the correct database path
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.db_path = os.path.join(project_root, 'src', 'database', 'data', 'fashion_trends.db')
        else:
            self.db_path = db_path

        self.engine = None
        self.conn = None

        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def create_connection(self):
        """Create a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"Connection to SQLite database successful at {self.db_path}")
            return self.conn
        except Exception as e:
            print(f"Error connecting to SQLite database: {e}")
            return None

    def setup_database(self, schema_file='sql/schema.sql'):
        """Set up the database using the SQL schema file."""
        try:
            # Create a new connection for setup
            conn = sqlite3.connect(self.db_path)

            # Get the absolute path to the schema file
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            schema_path = os.path.join(project_root, schema_file)

            # Check if schema file exists
            if not os.path.exists(schema_path):
                print(f"Schema file not found at: {schema_path}")
                return False

            print(f"Reading schema from: {schema_path}")

            with open(schema_path, 'r') as file:
                sql_commands = file.read()

            cursor = conn.cursor()
            cursor.executescript(sql_commands)

            conn.commit()
            print("SQLite database setup successful")

            # Verify tables were created
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Created tables: {tables}")

            return True
        except Exception as e:
            print(f"Error setting up database: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def create_sqlalchemy_engine(self):
        """Create a SQLAlchemy engine for database operations."""
        connection_string = f"sqlite:///{self.db_path}"
        try:
            self.engine = create_engine(connection_string)
            print("SQLAlchemy engine created successfully")
            return self.engine
        except Exception as e:
            print(f"Error creating SQLAlchemy engine: {e}")
            return None

    def test_connection(self):
        """Test the database connection and show tables."""
        try:
            conn = sqlite3.connect(self.db_path)  # Create a new connection for testing
            cursor = conn.cursor()

            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            print("\nTables in the database:")
            for table in tables:
                print(f"- {table[0]}")

            # Get count of records in each table
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"  Records in {table[0]}: {count}")

            return True
        except Exception as e:
            print(f"Error testing connection: {e}")
            return False
        finally:
            if conn:
                conn.close()


# For testing
if __name__ == "__main__":
    db = DatabaseManager()
    db.setup_database()
    engine = db.create_sqlalchemy_engine()

    if engine:
        print("\nDatabase setup complete. Ready for data collection.")
        db.test_connection()