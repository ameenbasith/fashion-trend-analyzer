# src/data_collection/instagram_scraper.py

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import os
import sys
import sqlite3

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.database_setup import DatabaseManager


class InstagramHashtagScraper:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = 'https://www.instagram.com/explore/tags/{}/'

    def scrape_hashtag(self, hashtag):
        """Scrape posts from a specific hashtag."""
        try:
            # This is a simplified example - real Instagram scraping requires more complex handling
            url = self.base_url.format(hashtag.strip('#'))
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                # Parse the page for post data
                posts = self.extract_posts(response.text)
                return posts
            else:
                print(f"Failed to scrape {hashtag}: Status {response.status_code}")
                return []

        except Exception as e:
            print(f"Error scraping {hashtag}: {e}")
            return []

    def extract_posts(self, html_content):
        """Extract post data from HTML - simplified example."""
        # This is a placeholder - real Instagram scraping is more complex
        # For now, let's return mock data
        mock_posts = [
            {
                'platform': 'instagram',
                'post_url': 'https://instagram.com/p/example1',
                'username': 'fashionista1',
                'followers': 15000,
                'caption': 'Love my new baggy jeans! #baggyjeans #streetwear #fashion',
                'likes': 1250,
                'comments': 85,
                'shares': 0,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'platform': 'instagram',
                'post_url': 'https://instagram.com/p/example2',
                'username': 'streetstylepro',
                'followers': 45000,
                'caption': 'Vintage vibes today #vintage #thrifted #y2kfashion',
                'likes': 3200,
                'comments': 210,
                'shares': 0,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        return mock_posts

    def save_posts(self, posts):
        """Save posts to the database."""
        try:
            # Use the correct database path from DatabaseManager
            engine = self.db_manager.create_sqlalchemy_engine()

            with engine.connect() as conn:
                from sqlalchemy import text

                sql_insert = text("""
                INSERT INTO social_posts 
                (platform, post_url, username, followers, caption, likes, comments, shares, created_at)
                VALUES (:platform, :post_url, :username, :followers, :caption, :likes, :comments, :shares, :created_at)
                """)

                for post in posts:
                    conn.execute(sql_insert, post)

                conn.commit()
                print(f"Successfully saved {len(posts)} posts")

        except Exception as e:
            print(f"Error saving posts: {e}")

if __name__ == "__main__":
    db = DatabaseManager()
    scraper = InstagramHashtagScraper(db)

    # Scrape some fashion hashtags
    hashtags = ['#streetwear', '#baggyjeans', '#vintage', '#y2kfashion']

    for hashtag in hashtags:
        print(f"Scraping {hashtag}...")
        posts = scraper.scrape_hashtag(hashtag)
        scraper.save_posts(posts)
        time.sleep(random.uniform(2, 5))  # Be nice to the server

    print("Scraping complete!")