# src/data_collection/reddit_scraper.py

import praw
import pandas as pd
import re
import time
from datetime import datetime, timedelta
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.database_setup import DatabaseManager


class RedditFashionScraper:
    def __init__(self, client_id, client_secret, user_agent, db_manager, username=None, password=None):
        # If username and password are provided, use password flow
        if username and password:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                username=username,
                password=password
            )
        # Otherwise use read-only mode
        else:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                check_for_async=False,  # Add this to avoid warning
                read_only=True  # Explicitly set read-only mode
            )

        print(f"Authenticated: {self.reddit.read_only}")

        self.db_manager = db_manager

        # Fashion-related subreddits
        self.fashion_subreddits = [
            'streetwear',
            'malefashionadvice',
            'femalefashionadvice',
            'malefashion',
            'womensstreetwear',
            'sneakers',
            'frugalmalefashion',
            'rawdenim',
            'fashionreps',
            'thriftstorehauls',
            'outfits',
            'styleboards'
        ]

        # Fashion keywords to track
        self.fashion_keywords = [
            'baggy', 'oversized', 'fitted', 'vintage', 'retro', 'y2k',
            'minimalist', 'streetwear', 'techwear', 'workwear', 'athleisure',
            'preppy', 'formal', 'casual', 'grunge', 'bohemian', 'aesthetic',
            'cottagecore', 'darkacademia', 'normcore', 'gorpcore'
        ]

        # Fashion brands to track
        self.fashion_brands = [
            'nike', 'adidas', 'zara', 'h&m', 'uniqlo', 'levi\'s', 'gap',
            'carhartt', 'patagonia', 'north face', 'supreme', 'vans', 'converse',
            'new balance', 'ralph lauren', 'gucci', 'prada', 'louis vuitton',
            'balenciaga', 'yeezy', 'asos', 'shein', 'urban outfitters'
        ]

    def extract_fashion_terms(self, text):
        """Extract fashion-related terms from text."""
        text = text.lower()

        # Find hashtags (sometimes used in Reddit too)
        hashtags = re.findall(r'#(\w+)', text)

        # Find fashion keywords
        keywords = []
        for keyword in self.fashion_keywords:
            if keyword.lower() in text:
                keywords.append(keyword)

        # Find fashion brands
        brands = []
        for brand in self.fashion_brands:
            if brand.lower() in text:
                brands.append(brand)

        return hashtags, keywords, brands

    def scrape_subreddit(self, subreddit_name, time_filter='month', limit=100):
        """Scrape posts from a subreddit."""
        try:
            print(f"Scraping r/{subreddit_name}...")
            subreddit = self.reddit.subreddit(subreddit_name)

            posts_data = []

            # Get top posts
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                # Skip posts with no text
                if not post.selftext and not post.title:
                    continue

                # Combine title and selftext for analysis
                full_text = f"{post.title} {post.selftext}"

                # Extract fashion terms
                hashtags, keywords, brands = self.extract_fashion_terms(full_text)

                # Skip posts with no fashion terms
                if not hashtags and not keywords and not brands:
                    continue

                # Create post data
                post_data = {
                    'platform': 'Reddit',
                    'post_url': f"https://www.reddit.com{post.permalink}",
                    'username': post.author.name if post.author else '[deleted]',
                    'followers': 0,  # Reddit doesn't have follower counts for regular users
                    'caption': full_text[:500],  # Limit to 500 chars
                    'likes': post.score,
                    'comments': post.num_comments,
                    'shares': 0,  # Reddit doesn't track shares
                    'created_at': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                    'subreddit': subreddit_name,
                    'hashtags': ', '.join(hashtags),
                    'keywords': ', '.join(keywords),
                    'brands': ', '.join(brands)
                }

                posts_data.append(post_data)

                # Get comments for this post
                post.comments.replace_more(limit=0)  # Skip "load more comments" links
                for comment in post.comments.list()[:20]:  # Get top comments
                    if hasattr(comment, 'body') and comment.body:
                        # Extract fashion terms from comment
                        comment_hashtags, comment_keywords, comment_brands = self.extract_fashion_terms(comment.body)

                        # Skip comments with no fashion terms
                        if not comment_hashtags and not comment_keywords and not comment_brands:
                            continue

                        # Create comment data
                        comment_data = {
                            'platform': 'Reddit',
                            'post_url': f"https://www.reddit.com{post.permalink}{comment.id}",
                            'username': comment.author.name if comment.author else '[deleted]',
                            'followers': 0,
                            'caption': comment.body[:500],  # Limit to 500 chars
                            'likes': comment.score,
                            'comments': 0,  # Comments don't have nested count
                            'shares': 0,
                            'created_at': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                            'subreddit': subreddit_name,
                            'hashtags': ', '.join(comment_hashtags),
                            'keywords': ', '.join(comment_keywords),
                            'brands': ', '.join(comment_brands)
                        }

                        posts_data.append(comment_data)

                # Sleep to avoid rate limits
                time.sleep(0.5)

            return posts_data

        except Exception as e:
            print(f"Error scraping r/{subreddit_name}: {e}")
            return []

    def save_to_database(self, posts_data):
        """Save the scraped data to the database."""
        if not posts_data:
            print("No data to save.")
            return 0

        conn = self.db_manager.create_connection()
        cursor = conn.cursor()

        # Add fashion keywords and brands columns if they don't exist
        try:
            cursor.execute("SELECT hashtags FROM social_posts LIMIT 1")
        except:
            # Add new columns if they don't exist
            try:
                cursor.execute("ALTER TABLE social_posts ADD COLUMN subreddit TEXT")
                cursor.execute("ALTER TABLE social_posts ADD COLUMN hashtags TEXT")
                cursor.execute("ALTER TABLE social_posts ADD COLUMN keywords TEXT")
                cursor.execute("ALTER TABLE social_posts ADD COLUMN brands TEXT")
                print("Added new columns to social_posts table")
            except Exception as e:
                print(f"Error adding columns: {e}")

        # Save posts
        count = 0
        for post in posts_data:
            try:
                cursor.execute("""
                INSERT INTO social_posts 
                (platform, post_url, username, followers, caption, likes, comments, shares, created_at, 
                subreddit, hashtags, keywords, brands)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post['platform'],
                    post['post_url'],
                    post['username'],
                    post['followers'],
                    post['caption'],
                    post['likes'],
                    post['comments'],
                    post['shares'],
                    post['created_at'],
                    post.get('subreddit', ''),
                    post.get('hashtags', ''),
                    post.get('keywords', ''),
                    post.get('brands', '')
                ))
                count += 1
            except Exception as e:
                print(f"Error saving post: {e}")

        conn.commit()
        conn.close()

        return count

    def analyze_and_save_trends(self):
        """Analyze the posts to extract trend data and save to database."""
        conn = self.db_manager.create_connection()

        # Get the posts
        posts_df = pd.read_sql_query("SELECT * FROM social_posts WHERE platform = 'Reddit'", conn)

        if posts_df.empty:
            print("No Reddit posts found for trend analysis.")
            conn.close()
            return 0

        # Prepare trend data
        trend_data = []
        today = datetime.now().strftime('%Y-%m-%d')

        # Process hashtags
        if 'hashtags' in posts_df.columns and not posts_df['hashtags'].isna().all():
            all_hashtags = []
            for hashtags_str in posts_df['hashtags'].dropna():
                hashtags = [h.strip() for h in hashtags_str.split(',') if h.strip()]
                all_hashtags.extend(hashtags)

            for hashtag in set(all_hashtags):
                count = all_hashtags.count(hashtag)
                score = count * 1.5  # Simple scoring based on occurrence
                trend_data.append(('hashtag:' + hashtag, score, 'Reddit', today))

        # Process keywords
        if 'keywords' in posts_df.columns and not posts_df['keywords'].isna().all():
            all_keywords = []
            for keywords_str in posts_df['keywords'].dropna():
                keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
                all_keywords.extend(keywords)

            for keyword in set(all_keywords):
                count = all_keywords.count(keyword)
                score = count * 1.2  # Simple scoring based on occurrence
                trend_data.append((keyword, score, 'Reddit', today))

        # Process brands
        if 'brands' in posts_df.columns and not posts_df['brands'].isna().all():
            all_brands = []
            for brands_str in posts_df['brands'].dropna():
                brands = [b.strip() for b in brands_str.split(',') if b.strip()]
                all_brands.extend(brands)

            for brand in set(all_brands):
                count = all_brands.count(brand)
                score = count * 1.0  # Simple scoring based on occurrence
                trend_data.append(('brand:' + brand, score, 'Reddit', today))

        # Save trend data
        cursor = conn.cursor()
        for trend_name, score, platform, date in trend_data:
            try:
                cursor.execute("""
                INSERT INTO trend_history (trend_name, score, platform, date_recorded)
                VALUES (?, ?, ?, ?)
                """, (trend_name, score, platform, date))
            except Exception as e:
                print(f"Error saving trend {trend_name}: {e}")

        conn.commit()
        conn.close()

        return len(trend_data)

    def run_full_scrape(self):
        """Run the full scraping process for all subreddits."""
        all_posts = []

        for subreddit in self.fashion_subreddits:
            posts = self.scrape_subreddit(subreddit)
            all_posts.extend(posts)
            print(f"Scraped {len(posts)} posts/comments from r/{subreddit}")
            time.sleep(2)  # Be nice to Reddit's servers

        total_saved = self.save_to_database(all_posts)
        print(f"Saved {total_saved} posts/comments to database")

        trends_saved = self.analyze_and_save_trends()
        print(f"Extracted and saved {trends_saved} trends")

        return total_saved, trends_saved


if __name__ == "__main__":
    # Set up your Reddit API credentials
    client_id = "InDg3bzNsa_lO7IRL185g"
    client_secret = "yOE4CV2ak_LMcYfDPG1e9YHL4PCD5g"
    user_agent = "script:fashion_trend_analyzer:v1.0 (by /u/TheCleanBeanDream)"

    # You can provide username/password for full access, or leave as None for read-only
    username = None  # Your Reddit username if you want to use it
    password = None  # Your Reddit password if you want to use it

    db = DatabaseManager()
    scraper = RedditFashionScraper(client_id, client_secret, user_agent, db, username, password)

    # Test connection first
    print("Testing Reddit API connection...")
    try:
        subreddit = scraper.reddit.subreddit("python")
        for post in subreddit.hot(limit=1):
            print(f"Successfully accessed Reddit API! Found post: {post.title}")
        print("Connection test successful!")
    except Exception as e:
        print(f"Connection test failed: {e}")

    # Only proceed if you want to after the test
    proceed = input("Continue with full scrape? (y/n): ")
    if proceed.lower() == 'y':
        posts_saved, trends_saved = scraper.run_full_scrape()
        print(f"\nComplete! Saved {posts_saved} posts and {trends_saved} trends.")
    else:
        print("Scrape cancelled.")