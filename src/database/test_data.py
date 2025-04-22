import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import os


def check_database_content(db_path='data/fashion_trends.db'):
    """Check the contents of the database."""
    try:
        # Get the absolute path to the database
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_db_path = os.path.join(project_root, db_path)

        print(f"Checking database at: {full_db_path}")

        conn = sqlite3.connect(full_db_path)

        # Get all brands
        brands_df = pd.read_sql_query("SELECT * FROM brands", conn)
        print("\nBrands:")
        print(brands_df)

        # Get all categories
        categories_df = pd.read_sql_query("SELECT * FROM categories", conn)
        print("\nCategories:")
        print(categories_df)

        # Get all products
        products_df = pd.read_sql_query("""
            SELECT p.*, b.brand_name, c.category_name 
            FROM products p
            LEFT JOIN brands b ON p.brand_id = b.brand_id
            LEFT JOIN categories c ON p.category_id = c.category_id
        """, conn)
        print("\nProducts:")
        print(products_df)

        # Get price history
        prices_df = pd.read_sql_query("""
            SELECT ph.*, p.product_name 
            FROM price_history ph
            LEFT JOIN products p ON ph.product_id = p.product_id
        """, conn)
        print("\nPrice History:")
        print(prices_df)

        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")


if __name__ == "__main__":
    check_database_content()