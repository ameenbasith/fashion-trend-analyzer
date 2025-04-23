# src/data_collection/data_generator.py

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import sqlite3

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.database_setup import DatabaseManager


class FashionTrendDataGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager

        # Define realistic fashion trend data
        self.platforms = ['Instagram', 'TikTok', 'Pinterest']

        self.fashion_hashtags = [
            '#streetwear', '#vintagestyle', '#y2kfashion', '#baggyfit',
            '#cargopants', '#minimalstyle', '#aestheticoutfit', '#denimjacket',
            '#platformboots', '#cubanlink', '#oversized', '#grunge',
            '#cottagecore', '#darkacademia', '#techwear', '#businesscasual'
        ]

        self.fashion_keywords = [
            'baggy', 'vintage', 'y2k', 'oversized', 'minimalist',
            'aesthetic', 'retro', 'grunge', 'preppy', 'casual',
            'bohemian', 'sustainable', 'thrifted', 'athleisure', 'highwaisted'
        ]

        self.brand_mentions = [
            'Zara', 'H&M', 'Nike', 'Adidas', 'Urban Outfitters',
            'Shein', 'Asos', 'Levi\'s', 'New Balance', 'Uniqlo',
            'Thrasher', 'Carhartt', 'Converse', 'Dickies', 'Vans'
        ]

        self.influencers = [
            ('fashion_guru', 1500000),
            ('style_maven', 750000),
            ('trendsetter101', 2100000),
            ('outfitdaily', 950000),
            ('stylistpick', 1250000),
            ('vintage_vibes', 550000),
            ('streetwear_daily', 1800000),
            ('minimal_fits', 620000),
            ('thrift_queen', 890000),
            ('high_fashion_low_cost', 1050000)
        ]

    def generate_trend_growth(self, days=30, num_trends=8):
        """Generate trend growth data over time."""
        # Start date
        start_date = datetime.now() - timedelta(days=days)

        # Select random trends to track
        selected_trends = random.sample(self.fashion_hashtags, min(num_trends, len(self.fashion_hashtags)))

        # Generate growth data
        trend_data = []

        for trend in selected_trends:
            # Initial score (1-5)
            base_score = random.uniform(1.0, 5.0)

            # Growth pattern - choose between steady growth, viral spike, or decline
            pattern = random.choice(['steady', 'viral', 'decline'])

            for day in range(days):
                date = start_date + timedelta(days=day)

                # Calculate score based on pattern
                if pattern == 'steady':
                    # Steady linear growth with small fluctuations
                    growth = day * 0.15
                    fluctuation = random.uniform(-0.5, 0.5)
                    score = base_score + growth + fluctuation

                elif pattern == 'viral':
                    # Viral spike (exponential growth after a certain point)
                    if day < days * 0.7:  # First 70% of days: slow growth
                        growth = day * 0.1
                        fluctuation = random.uniform(-0.3, 0.3)
                    else:  # Last 30% of days: rapid growth
                        growth = (day * 0.5) ** 1.5
                        fluctuation = random.uniform(-0.5, 0.5)
                    score = base_score + growth + fluctuation

                else:  # 'decline'
                    # Initial popularity that declines
                    initial_boost = days * 0.3  # Initial boost
                    decline = day * 0.2  # Decline rate
                    fluctuation = random.uniform(-0.4, 0.4)
                    score = (base_score + initial_boost) - decline + fluctuation

                # Ensure score stays positive
                score = max(0.1, score)

                # Add to trend data
                trend_data.append({
                    'trend_name': trend,
                    'score': round(score, 2),
                    'platform': random.choice(self.platforms),
                    'date_recorded': date.strftime('%Y-%m-%d'),
                    'pattern': pattern
                })

        return pd.DataFrame(trend_data)

    def generate_social_posts(self, num_posts=100):
        """Generate realistic social media posts."""
        posts = []

        for _ in range(num_posts):
            # Select a random influencer
            username, followers = random.choice(self.influencers)

            # Random number of likes, comments and shares
            engagement_rate = random.uniform(0.01, 0.1)  # 1% to 10% engagement
            likes = int(followers * engagement_rate * random.uniform(0.5, 1.5))
            comments = int(likes * random.uniform(0.05, 0.2))
            shares = int(likes * random.uniform(0.01, 0.1))

            # Generate caption with hashtags and keywords
            num_hashtags = random.randint(2, 5)
            hashtags = random.sample(self.fashion_hashtags, num_hashtags)

            keywords = []
            for keyword in random.sample(self.fashion_keywords, random.randint(1, 3)):
                if random.random() < 0.7:  # 70% chance to include a keyword
                    keywords.append(keyword)

            brand = ""
            if random.random() < 0.4:  # 40% chance to mention a brand
                brand = random.choice(self.brand_mentions)

            # Build caption
            caption_templates = [
                f"Loving this {random.choice(self.fashion_keywords)} look! {' '.join(hashtags)}",
                f"Today's outfit featuring {brand}. What do you think? {' '.join(hashtags)}",
                f"New thrift find - {random.choice(self.fashion_keywords)} vibes! {' '.join(hashtags)}",
                f"{brand} never disappoints! Perfect for {random.choice(self.fashion_keywords)} style. {' '.join(hashtags)}",
                f"My go-to {random.choice(self.fashion_keywords)} look for the season. {' '.join(hashtags)}"
            ]

            caption = random.choice(caption_templates)

            # Random date within last 30 days
            days_ago = random.randint(0, 30)
            post_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')

            posts.append({
                'platform': random.choice(self.platforms),
                'post_url': f"https://{random.choice(self.platforms).lower()}.com/p/{username}_{random.randint(10000, 99999)}",
                'username': username,
                'followers': followers,
                'caption': caption,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'created_at': post_date
            })

        return pd.DataFrame(posts)

    def save_to_database(self):
        """Generate and save data to the database."""
        # Generate trend data
        trend_df = self.generate_trend_growth(days=30, num_trends=10)

        # Generate social posts
        posts_df = self.generate_social_posts(num_posts=50)

        # Save to database
        conn = self.db_manager.create_connection()
        cursor = conn.cursor()

        # Save trend data
        for _, row in trend_df.iterrows():
            try:
                cursor.execute("""
                INSERT INTO trend_history (trend_name, score, platform, date_recorded)
                VALUES (?, ?, ?, ?)
                """, (row['trend_name'], row['score'], row['platform'], row['date_recorded']))
            except sqlite3.IntegrityError:
                # Skip if record already exists with same trend and date
                pass

        # Save social posts
        for _, row in posts_df.iterrows():
            cursor.execute("""
            INSERT INTO social_posts 
            (platform, post_url, username, followers, caption, likes, comments, shares, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['platform'],
                row['post_url'],
                row['username'],
                row['followers'],
                row['caption'],
                row['likes'],
                row['comments'],
                row['shares'],
                row['created_at']
            ))

        conn.commit()
        conn.close()

        return len(trend_df), len(posts_df)


if __name__ == "__main__":
    db = DatabaseManager()
    generator = FashionTrendDataGenerator(db)

    num_trends, num_posts = generator.save_to_database()

    print(f"Generated and saved {num_trends} trend records and {num_posts} social posts!")
    print(f"Your database now has more realistic fashion trend data for analysis.")