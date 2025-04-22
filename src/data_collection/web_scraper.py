import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
from datetime import datetime
import re


class FashionScraper:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_delay = 3  # Base delay between requests in seconds

    def random_delay(self):
        """Add random delay between requests to avoid being blocked."""
        time.sleep(self.base_delay + random.uniform(1, 3))

    def clean_price(self, price_text):
        """Extract numerical price from price text."""
        if not price_text:
            return None

        # Remove currency symbols and extract numbers
        price_match = re.search(r'(\d+(?:\.\d{2})?)', price_text.replace(',', ''))
        if price_match:
            return float(price_match.group(1))
        return None

    def scrape_product_details(self, url):
        """Scrape product details from a given URL."""
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self.parse_product_page(soup, url)
            else:
                print(f"Failed to retrieve {url}. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def parse_product_page(self, soup, url):
        """Parse product information from the page. This should be customized for each website."""
        # This is a generic parser - you'll need to customize it for specific websites
        product_data = {
            'url': url,
            'name': None,
            'price': None,
            'sale_price': None,
            'description': None,
            'category': None,
            'brand': None,
            'material': None,
            'gender': None,
            'scrape_date': datetime.now().strftime('%Y-%m-%d')
        }

        # Example selectors - these need to be customized for each website
        # product_data['name'] = soup.select_one('.product-name')
        # product_data['price'] = soup.select_one('.product-price')
        # etc.

        return product_data

    def save_to_database(self, product_data):
        """Save scraped product data to the database."""
        try:
            engine = self.db_manager.create_sqlalchemy_engine()

            with engine.connect() as conn:
                from sqlalchemy import text

                # First, insert brand if it doesn't exist
                brand_insert = text("""
                INSERT OR IGNORE INTO brands (brand_name) VALUES (:brand_name)
                """)
                conn.execute(brand_insert, {'brand_name': product_data['brand']})

                # Get brand_id
                brand_id_query = text("SELECT brand_id FROM brands WHERE brand_name = :brand_name")
                result = conn.execute(brand_id_query, {'brand_name': product_data['brand']})
                brand_id = result.fetchone()[0]

                # Similar logic for category
                category_insert = text("""
                INSERT OR IGNORE INTO categories (category_name) VALUES (:category_name)
                """)
                conn.execute(category_insert, {'category_name': product_data['category']})

                category_id_query = text("SELECT category_id FROM categories WHERE category_name = :category_name")
                result = conn.execute(category_id_query, {'category_name': product_data['category']})
                category_id = result.fetchone()[0]

                # Insert product
                product_insert = text("""
                INSERT INTO products (product_name, brand_id, category_id, description, material, gender)
                VALUES (:product_name, :brand_id, :category_id, :description, :material, :gender)
                """)
                result = conn.execute(product_insert, {
                    'product_name': product_data['name'],
                    'brand_id': brand_id,
                    'category_id': category_id,
                    'description': product_data['description'],
                    'material': product_data['material'],
                    'gender': product_data['gender']
                })

                # Get the last inserted product_id
                product_id_query = text("SELECT last_insert_rowid()")
                product_id = conn.execute(product_id_query).fetchone()[0]

                # Insert price history
                price_insert = text("""
                INSERT INTO price_history (product_id, price, sale_price, date_recorded)
                VALUES (:product_id, :price, :sale_price, :date_recorded)
                """)
                conn.execute(price_insert, {
                    'product_id': product_id,
                    'price': product_data['price'],
                    'sale_price': product_data['sale_price'],
                    'date_recorded': product_data['scrape_date']
                })

                # Commit the transaction
                conn.commit()

            return True
        except Exception as e:
            print(f"Error saving to database: {e}")
            return False

    def scrape_sample_data(self):
        """Create sample data to test the scraper with current fashion trends."""
        # Modern, trendy sample data
        sample_products = [
            {
                'name': 'Oversized Baggy Jeans',
                'price': 89.99,
                'sale_price': None,
                'description': 'Wide-leg, relaxed fit jeans with distressed details',
                'category': 'Jeans',
                'brand': 'UrbanSkate',
                'material': 'Denim',
                'gender': 'Unisex',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'name': 'Designer Denim Jorts',
                'price': 79.99,
                'sale_price': 69.99,
                'description': 'Premium denim shorts with frayed hem, perfect for summer',
                'category': 'Shorts',
                'brand': 'DenimLab',
                'material': 'Premium Denim',
                'gender': 'Men',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'name': 'Varsity Football Jersey',
                'price': 129.99,
                'sale_price': None,
                'description': 'Authentic mesh athletic jersey with bold numbering',
                'category': 'Jerseys',
                'brand': 'SportLux',
                'material': 'Polyester Mesh',
                'gender': 'Unisex',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'name': 'Cuban Link Chain',
                'price': 249.99,
                'sale_price': 199.99,
                'description': 'Gold-plated Miami Cuban link chain, 8mm width',
                'category': 'Jewelry',
                'brand': 'IcedOut',
                'material': 'Stainless Steel/Gold Plated',
                'gender': 'Unisex',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'name': 'Classic Polo Shirt',
                'price': 59.99,
                'sale_price': None,
                'description': 'Slim fit polo with embroidered logo',
                'category': 'Polos',
                'brand': 'PrepStyle',
                'material': 'Pique Cotton',
                'gender': 'Men',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'name': 'Y2K Cargo Pants',
                'price': 79.99,
                'sale_price': None,
                'description': 'Loose-fit cargo pants with multiple pockets',
                'category': 'Pants',
                'brand': 'RetroRevival',
                'material': 'Cotton Blend',
                'gender': 'Women',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'name': 'Chunky Platform Sneakers',
                'price': 149.99,
                'sale_price': None,
                'description': 'Retro-inspired chunky sneakers with platform sole',
                'category': 'Shoes',
                'brand': 'StreetKix',
                'material': 'Leather/Mesh',
                'gender': 'Unisex',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'name': 'Layered Pearl Necklace',
                'price': 45.99,
                'sale_price': 39.99,
                'description': 'Multi-strand freshwater pearl choker',
                'category': 'Jewelry',
                'brand': 'PearlEssence',
                'material': 'Freshwater Pearls',
                'gender': 'Women',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            }
        ]

        for product in sample_products:
            success = self.save_to_database(product)
            if success:
                print(f"Successfully saved: {product['name']}")
            else:
                print(f"Failed to save: {product['name']}")


# For testing
if __name__ == "__main__":
    import sys
    import os

    # Add the project root directory to the path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_root)

    from src.database.database_setup import DatabaseManager

    db = DatabaseManager()

    # Check if database exists, if not, set it up
    if not os.path.exists('data/fashion_trends.db'):
        print("Setting up database...")
        success = db.setup_database()
        if not success:
            print("Database setup failed. Cannot continue.")
            exit(1)

    scraper = FashionScraper(db)

    # Test with sample data
    print("\nStarting to scrape sample data...")
    scraper.scrape_sample_data()

    # Test the data
    print("\nChecking database contents...")
    db.test_connection()