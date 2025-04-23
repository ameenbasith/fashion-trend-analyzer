# src/data_collection/enhanced_data_generator.py

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import sqlite3
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.database_setup import DatabaseManager


class EnhancedFashionDataGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager

        # Load real fashion trend data from JSON
        self.trend_data = self.load_real_trend_data()

        # Define social media platforms
        self.platforms = ['Instagram', 'TikTok', 'Pinterest']

        # Define influencer profiles with realistic follower counts
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

    def load_real_trend_data(self):
        """Load real fashion trend data from JSON file."""
        try:
            # Path to the real trend data file
            data_file = os.path.join(project_root, 'data', 'real_fashion_trends.json')

            # If file doesn't exist, create it with sample data
            if not os.path.exists(data_file):
                print("Creating sample fashion trend data...")

                # Real fashion trend data as of 2023-2024
                real_trends = {
                    "current_trends": [
                        {"name": "#baggyfit", "score": 9.2, "growth": "high", "category": "streetwear"},
                        {"name": "#y2kfashion", "score": 8.9, "growth": "high", "category": "vintage"},
                        {"name": "#oversizedeverything", "score": 8.5, "growth": "medium", "category": "streetwear"},
                        {"name": "#cargopants", "score": 8.3, "growth": "high", "category": "streetwear"},
                        {"name": "#darkacademia", "score": 7.9, "growth": "medium", "category": "aesthetic"},
                        {"name": "#platformboots", "score": 7.8, "growth": "medium", "category": "footwear"},
                        {"name": "#cottagecore", "score": 7.6, "growth": "medium", "category": "aesthetic"},
                        {"name": "#genderlessfashion", "score": 7.5, "growth": "high", "category": "concept"},
                        {"name": "#vintagedenim", "score": 7.4, "growth": "medium", "category": "vintage"},
                        {"name": "#sustainablestyle", "score": 7.2, "growth": "high", "category": "concept"},
                        {"name": "#denimonstyle", "score": 7.0, "growth": "medium", "category": "fabric"},
                        {"name": "#gorpcore", "score": 6.9, "growth": "high", "category": "outdoor"},
                        {"name": "#croptop", "score": 6.8, "growth": "medium", "category": "tops"},
                        {"name": "#cubanlink", "score": 6.7, "growth": "medium", "category": "accessories"},
                        {"name": "#minimalstyle", "score": 6.6, "growth": "medium", "category": "aesthetic"},
                        {"name": "#cleanaesthetic", "score": 6.5, "growth": "medium", "category": "aesthetic"},
                        {"name": "#thriftfinds", "score": 6.4, "growth": "high", "category": "shopping"},
                        {"name": "#cowboyboots", "score": 6.3, "growth": "medium", "category": "footwear"},
                        {"name": "#balletcore", "score": 6.2, "growth": "medium", "category": "aesthetic"},
                        {"name": "#leatherjacket", "score": 6.0, "growth": "medium", "category": "outerwear"}
                    ],
                    "brands": [
                        {"name": "Zara", "popularity": 8.7, "growth": "medium", "category": "fast-fashion"},
                        {"name": "H&M", "popularity": 8.5, "growth": "medium", "category": "fast-fashion"},
                        {"name": "Nike", "popularity": 9.1, "growth": "medium", "category": "sportswear"},
                        {"name": "Adidas", "popularity": 8.9, "growth": "medium", "category": "sportswear"},
                        {"name": "Shein", "popularity": 8.8, "growth": "high", "category": "fast-fashion"},
                        {"name": "Urban Outfitters", "popularity": 7.9, "growth": "medium", "category": "retail"},
                        {"name": "Levi's", "popularity": 8.3, "growth": "medium", "category": "denim"},
                        {"name": "Uniqlo", "popularity": 8.4, "growth": "high", "category": "basics"},
                        {"name": "New Balance", "popularity": 8.6, "growth": "high", "category": "footwear"},
                        {"name": "Carhartt", "popularity": 8.2, "growth": "high", "category": "workwear"},
                        {"name": "The North Face", "popularity": 8.0, "growth": "medium", "category": "outdoor"},
                        {"name": "Patagonia", "popularity": 7.8, "growth": "medium", "category": "outdoor"},
                        {"name": "Dickies", "popularity": 7.6, "growth": "medium", "category": "workwear"},
                        {"name": "Vans", "popularity": 7.9, "growth": "medium", "category": "footwear"},
                        {"name": "Converse", "popularity": 7.8, "growth": "medium", "category": "footwear"}
                    ],
                    "styles": [
                        {"name": "Baggy", "popularity": 9.3, "growth": "high", "category": "fit"},
                        {"name": "Y2K", "popularity": 9.0, "growth": "high", "category": "retro"},
                        {"name": "Vintage", "popularity": 8.8, "growth": "medium", "category": "retro"},
                        {"name": "Minimalist", "popularity": 8.5, "growth": "medium", "category": "aesthetic"},
                        {"name": "Streetwear", "popularity": 8.7, "growth": "medium", "category": "urban"},
                        {"name": "Athleisure", "popularity": 8.6, "growth": "medium", "category": "sportswear"},
                        {"name": "Sustainable", "popularity": 8.4, "growth": "high", "category": "concept"},
                        {"name": "Gender-neutral", "popularity": 8.3, "growth": "high", "category": "concept"},
                        {"name": "Workwear", "popularity": 8.1, "growth": "high", "category": "functional"},
                        {"name": "Gorpcore", "popularity": 7.9, "growth": "high", "category": "outdoor"},
                        {"name": "Coastal Grandmother", "popularity": 7.7, "growth": "medium", "category": "aesthetic"},
                        {"name": "Dopamine Dressing", "popularity": 7.6, "growth": "medium", "category": "concept"},
                        {"name": "Retro Revival", "popularity": 7.5, "growth": "medium", "category": "retro"},
                        {"name": "Upcycled", "popularity": 7.4, "growth": "high", "category": "sustainable"}
                    ],
                    "colors": [
                        {"name": "Neutrals", "popularity": 8.9, "growth": "medium", "category": "earthy"},
                        {"name": "Earth Tones", "popularity": 8.7, "growth": "medium", "category": "earthy"},
                        {"name": "Pastels", "popularity": 8.5, "growth": "medium", "category": "soft"},
                        {"name": "Bold Brights", "popularity": 8.3, "growth": "medium", "category": "vibrant"},
                        {"name": "Monochrome", "popularity": 8.2, "growth": "medium", "category": "minimal"}
                    ],
                    "fabrics": [
                        {"name": "Denim", "popularity": 9.0, "growth": "medium", "category": "classic"},
                        {"name": "Cotton", "popularity": 8.8, "growth": "medium", "category": "natural"},
                        {"name": "Leather", "popularity": 8.6, "growth": "medium", "category": "luxury"},
                        {"name": "Linen", "popularity": 8.5, "growth": "high", "category": "natural"},
                        {"name": "Recycled", "popularity": 8.3, "growth": "high", "category": "sustainable"}
                    ]
                }

                # Save to file
                os.makedirs(os.path.dirname(data_file), exist_ok=True)
                with open(data_file, 'w') as f:
                    json.dump(real_trends, f, indent=4)

                return real_trends

            # Load data from file
            with open(data_file, 'r') as f:
                return json.load(f)

        except Exception as e:
            print(f"Error loading trend data: {e}")
            # Return empty data structure
            return {
                "current_trends": [],
                "brands": [],
                "styles": [],
                "colors": [],
                "fabrics": []
            }

    def generate_trend_history(self, days=60):
        """Generate trend history data based on real trends."""
        # Start date
        start_date = datetime.now() - timedelta(days=days)

        # Generate trend data
        trend_data = []

        # Process hashtag trends
        for trend in self.trend_data["current_trends"]:
            # Initial score based on trend popularity
            base_score = trend["score"]

            # Growth pattern based on trend growth rate
            if trend["growth"] == "high":
                growth_factor = 0.04  # 4% daily growth
            elif trend["growth"] == "medium":
                growth_factor = 0.02  # 2% daily growth
            else:
                growth_factor = 0.01  # 1% daily growth

            for day in range(days):
                date = start_date + timedelta(days=day)

                # Calculate score with growth and random fluctuation
                growth = base_score * (1 + growth_factor) ** day
                fluctuation = random.uniform(-0.5, 0.5)
                score = growth + fluctuation

                # Ensure score stays within reasonable range
                score = max(1.0, min(10.0, score))

                # Add to trend data
                trend_data.append({
                    'trend_name': trend["name"],
                    'score': round(score, 2),
                    'platform': random.choice(self.platforms),
                    'date_recorded': date.strftime('%Y-%m-%d'),
                    'category': trend["category"]
                })

        # Process style trends
        for style in self.trend_data["styles"]:
            # Initial score based on style popularity
            base_score = style["popularity"]

            # Growth pattern based on style growth rate
            if style["growth"] == "high":
                growth_factor = 0.03  # 3% daily growth
            elif style["growth"] == "medium":
                growth_factor = 0.015  # 1.5% daily growth
            else:
                growth_factor = 0.005  # 0.5% daily growth

            for day in range(days):
                date = start_date + timedelta(days=day)

                # Calculate score with growth and random fluctuation
                growth = base_score * (1 + growth_factor) ** day
                fluctuation = random.uniform(-0.4, 0.4)
                score = growth + fluctuation

                # Ensure score stays within reasonable range
                score = max(1.0, min(10.0, score))

                # Add to trend data
                trend_data.append({
                    'trend_name': style["name"].lower(),  # No hashtag for style names
                    'score': round(score, 2),
                    'platform': random.choice(self.platforms),
                    'date_recorded': date.strftime('%Y-%m-%d'),
                    'category': style["category"]
                })

        # Process brand trends
        for brand in self.trend_data["brands"]:
            # Initial score based on brand popularity
            base_score = brand["popularity"]

            # Growth pattern based on brand growth rate
            if brand["growth"] == "high":
                growth_factor = 0.025  # 2.5% daily growth
            elif brand["growth"] == "medium":
                growth_factor = 0.01  # 1% daily growth
            else:
                growth_factor = 0.005  # 0.5% daily growth

            for day in range(days):
                date = start_date + timedelta(days=day)

                # Calculate score with growth and random fluctuation
                growth = base_score * (1 + growth_factor) ** day
                fluctuation = random.uniform(-0.3, 0.3)
                score = growth + fluctuation

                # Ensure score stays within reasonable range
                score = max(1.0, min(10.0, score))

                # Add to trend data (adding "brand:" prefix to distinguish brands)
                trend_data.append({
                    'trend_name': "brand:" + brand["name"],
                    'score': round(score, 2),
                    'platform': random.choice(self.platforms),
                    'date_recorded': date.strftime('%Y-%m-%d'),
                    'category': brand["category"]
                })

        return pd.DataFrame(trend_data)

    def generate_social_posts(self, num_posts=100):
        """Generate realistic social media posts based on current trends."""
        posts = []

        # Combine all fashion elements
        trends = [t["name"] for t in self.trend_data["current_trends"]]
        styles = [s["name"].lower() for s in self.trend_data["styles"]]
        brands = [b["name"] for b in self.trend_data["brands"]]
        colors = [c["name"].lower() for c in self.trend_data["colors"]]
        fabrics = [f["name"].lower() for f in self.trend_data["fabrics"]]

        for _ in range(num_posts):
            # Select a random influencer
            username, followers = random.choice(self.influencers)

            # Random number of likes, comments and shares
            engagement_rate = random.uniform(0.01, 0.1)  # 1% to 10% engagement
            likes = int(followers * engagement_rate * random.uniform(0.5, 1.5))
            comments = int(likes * random.uniform(0.05, 0.2))
            shares = int(likes * random.uniform(0.01, 0.1))

            # Pick random fashion elements
            used_trends = random.sample(trends, random.randint(1, 3))
            used_style = random.choice(styles)

            # Maybe include a brand (70% chance)
            if random.random() < 0.7:
                used_brand = random.choice(brands)
            else:
                used_brand = ""

            used_color = random.choice(colors)
            used_fabric = random.choice(fabrics)

            # Build caption with templates for more variety
            caption_templates = [
                f"Loving this {used_style} {used_color} look! {' '.join(used_trends)}",
                f"Today's {used_style} outfit featuring {used_brand}. What do you think? {' '.join(used_trends)}",
                f"New {used_fabric} find - {used_style} vibes! {' '.join(used_trends)}",
                f"{used_brand} never disappoints! Perfect for {used_style} style. {' '.join(used_trends)}",
                f"My go-to {used_style} look made with {used_fabric} in {used_color}. {' '.join(used_trends)}"
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
                'created_at': post_date,
                'hashtags': ', '.join([t for t in used_trends if t.startswith('#')]),
                'keywords': ', '.join(
                    [t for t in used_trends if not t.startswith('#')] + [used_style, used_color, used_fabric]),
                'brands': used_brand
            })

        return pd.DataFrame(posts)

    def save_to_database(self):
        """Generate and save realistic fashion data to the database."""
        # Generate trend history
        trend_df = self.generate_trend_history(days=60)

        # Generate social posts
        posts_df = self.generate_social_posts(num_posts=100)

        # Save to database
        conn = self.db_manager.create_connection()
        cursor = conn.cursor()

        # Add columns to tables if needed
        try:
            cursor.execute("SELECT category FROM trend_history LIMIT 1")
        except:
            try:
                cursor.execute("ALTER TABLE trend_history ADD COLUMN category TEXT")
                print("Added category column to trend_history table")
            except Exception as e:
                print(f"Error adding category column: {e}")

        # Save trend data
        for _, row in trend_df.iterrows():
            try:
                cursor.execute("""
                INSERT INTO trend_history (trend_name, score, platform, date_recorded, category)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    row['trend_name'],
                    row['score'],
                    row['platform'],
                    row['date_recorded'],
                    row.get('category', '')
                ))
            except sqlite3.IntegrityError:
                # Skip if record already exists with same trend and date
                pass

        # Check if social_posts table has the required columns
        try:
            cursor.execute("SELECT hashtags FROM social_posts LIMIT 1")
        except:
            try:
                cursor.execute("ALTER TABLE social_posts ADD COLUMN hashtags TEXT")
                cursor.execute("ALTER TABLE social_posts ADD COLUMN keywords TEXT")
                cursor.execute("ALTER TABLE social_posts ADD COLUMN brands TEXT")
                print("Added hashtags, keywords, and brands columns to social_posts table")
            except Exception as e:
                print(f"Error adding columns: {e}")

        # Save social posts
        for _, row in posts_df.iterrows():
            cursor.execute("""
            INSERT INTO social_posts 
            (platform, post_url, username, followers, caption, likes, comments, shares, created_at,
            hashtags, keywords, brands)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['platform'],
                row['post_url'],
                row['username'],
                row['followers'],
                row['caption'],
                row['likes'],
                row['comments'],
                row['shares'],
                row['created_at'],
                row.get('hashtags', ''),
                row.get('keywords', ''),
                row.get('brands', '')
            ))

        conn.commit()
        conn.close()

        return len(trend_df), len(posts_df)


if __name__ == "__main__":
    db = DatabaseManager()
    generator = EnhancedFashionDataGenerator(db)

    num_trends, num_posts = generator.save_to_database()

    print(f"Generated and saved {num_trends} trend records and {num_posts} social posts!")
    print(f"Your database now has realistic fashion trend data for machine learning.")