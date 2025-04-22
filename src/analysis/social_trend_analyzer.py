# src/analysis/social_trend_analyzer.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from collections import Counter
import re
from textblob import TextBlob


class SocialTrendAnalyzer:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.trending_hashtags = [
            '#streetwear', '#OOTD', '#fashiontrends',
            '#vintage', '#y2k', '#grwm', '#fashiontiktok'
        ]
        self.fashion_keywords = [
            'baggy', 'oversized', 'vintage', 'y2k', 'cargo',
            'platform', 'chunky', 'streetwear', 'aesthetic'
        ]

    def analyze_social_posts(self, posts_data):
        """Analyze social media posts for fashion trends."""
        trend_scores = Counter()

        for post in posts_data:
            # Extract hashtags
            hashtags = re.findall(r'#\w+', post['caption'])

            # Extract fashion keywords
            keywords = []
            for keyword in self.fashion_keywords:
                if keyword.lower() in post['caption'].lower():
                    keywords.append(keyword)

            # Calculate engagement rate
            engagement_rate = (post['likes'] + post['comments']) / post['followers']

            # Update trend scores based on engagement
            for tag in hashtags:
                trend_scores[tag] += engagement_rate * 10

            for keyword in keywords:
                trend_scores[keyword] += engagement_rate * 5

        return trend_scores

    def detect_emerging_trends(self, historical_data, current_data):
        """Detect which trends are emerging vs. declining."""
        emerging = {}
        declining = {}

        for trend, current_score in current_data.items():
            historical_score = historical_data.get(trend, 0)

            if historical_score > 0:
                growth_rate = (current_score - historical_score) / historical_score

                if growth_rate > 0.2:  # 20% growth
                    emerging[trend] = growth_rate
                elif growth_rate < -0.2:  # 20% decline
                    declining[trend] = growth_rate

        return emerging, declining

    def sentiment_analysis(self, posts_data):
        """Analyze sentiment around fashion items/brands."""
        sentiment_scores = {}

        for post in posts_data:
            analysis = TextBlob(post['caption'])

            # Extract mentioned brands
            mentioned_brands = []  # You'd implement brand detection here

            for brand in mentioned_brands:
                if brand not in sentiment_scores:
                    sentiment_scores[brand] = []

                sentiment_scores[brand].append(analysis.sentiment.polarity)

        # Average sentiment per brand
        average_sentiment = {}
        for brand, scores in sentiment_scores.items():
            average_sentiment[brand] = sum(scores) / len(scores)

        return average_sentiment

    def generate_trend_report(self, social_data):
        """Generate comprehensive trend report."""
        trend_scores = self.analyze_social_posts(social_data)

        # Get top trends
        top_trends = sorted(trend_scores.items(), key=lambda x: x[1], reverse=True)[:20]

        # Detect emerging vs declining
        # (You'd need historical data for this)

        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'top_trends': top_trends,
            'total_posts_analyzed': len(social_data),
            'categories': self.categorize_trends(top_trends)
        }

        return report

    def categorize_trends(self, trends):
        """Categorize trends into style categories."""
        categories = {
            'vintage': ['y2k', 'vintage', 'retro', '90s', '80s'],
            'streetwear': ['streetwear', 'baggy', 'oversized', 'skate'],
            'luxury': ['designer', 'luxury', 'couture', 'highfashion'],
            'casual': ['basic', 'minimal', 'casual', 'everyday']
        }

        categorized = {cat: [] for cat in categories}

        for trend, score in trends:
            for category, keywords in categories.items():
                if any(keyword in trend.lower() for keyword in keywords):
                    categorized[category].append((trend, score))

        return categorized


# Create database schema for social data
def create_social_schema():
    """Create schema for social media data."""
    schema = """
    CREATE TABLE IF NOT EXISTS social_posts (
        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,  -- instagram, tiktok, etc.
        post_url TEXT,
        username TEXT,
        followers INTEGER,
        caption TEXT,
        likes INTEGER,
        comments INTEGER,
        shares INTEGER,
        created_at TIMESTAMP,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS trend_history (
        trend_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trend_name TEXT NOT NULL,
        score FLOAT,
        platform TEXT,
        date_recorded DATE,
        UNIQUE(trend_name, platform, date_recorded)
    );

    CREATE TABLE IF NOT EXISTS influencer_mentions (
        mention_id INTEGER PRIMARY KEY AUTOINCREMENT,
        influencer_name TEXT,
        follower_count INTEGER,
        brand_mentioned TEXT,
        product_mentioned TEXT,
        sentiment_score FLOAT,
        engagement_rate FLOAT,
        date_posted DATE
    );
    """
    return schema


# Add this at the bottom of social_trend_analyzer.py

if __name__ == "__main__":
    from src.database.database_setup import DatabaseManager

    # Initialize database
    db = DatabaseManager()

    # Create social media schema
    schema_sql = create_social_schema()

    # Apply schema to database
    try:
        conn = db.create_connection()
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        print("Social media schema created successfully")
    except Exception as e:
        print(f"Error creating schema: {e}")
    finally:
        if conn:
            conn.close()

    # Create analyzer instance
    analyzer = SocialTrendAnalyzer(db)

    # Create sample social media data for testing
    sample_posts = [
        {
            'caption': 'Love these #baggyjeans and #oversized tees! #streetwear #y2kfashion',
            'likes': 1200,
            'comments': 85,
            'followers': 15000
        },
        {
            'caption': 'New #vintage finds! 90s denim is back #thrifted #sustainablefashion',
            'likes': 850,
            'comments': 62,
            'followers': 8000
        },
        {
            'caption': 'Platform sneakers + cargo pants = perfect combo #streetstyle #ootd',
            'likes': 2300,
            'comments': 145,
            'followers': 25000
        },
        {
            'caption': 'Cuban links are trending hard rn #jewelry #hiphopfashion #iced',
            'likes': 3100,
            'comments': 210,
            'followers': 45000
        },
        {
            'caption': 'Minimalist wardrobe essentials #capsulewardrobe #basics #minimal',
            'likes': 980,
            'comments': 54,
            'followers': 12000
        }
    ]

    # Analyze the sample posts
    trend_scores = analyzer.analyze_social_posts(sample_posts)

    print("\nTop Trending Items/Styles:")
    print("-" * 30)
    for trend, score in sorted(trend_scores.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{trend}: {score:.2f}")

    # Generate trend report
    report = analyzer.generate_trend_report(sample_posts)

    print("\nTrend Report:")
    print("-" * 30)
    print(f"Date: {report['date']}")
    print(f"Posts Analyzed: {report['total_posts_analyzed']}")
    print("\nTop Trends:")
    for trend, score in report['top_trends'][:10]:
        print(f"  {trend}: {score:.2f}")

    print("\nCategorized Trends:")
    for category, trends in report['categories'].items():
        print(f"\n{category.upper()}:")
        for trend, score in trends[:3]:  # Show top 3 per category
            print(f"  {trend}: {score:.2f}")