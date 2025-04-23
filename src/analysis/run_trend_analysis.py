# src/analysis/run_trend_analysis.py

import os
import sys
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.database_setup import DatabaseManager
from src.analysis.social_trend_analyzer import SocialTrendAnalyzer


def analyze_social_trends():
    """Run trend analysis on the collected social media data."""
    # Initialize database manager
    db = DatabaseManager()

    # Create analyzer
    analyzer = SocialTrendAnalyzer(db)

    # Get social media posts from database
    print("Fetching social media data...")
    conn = db.create_connection()

    posts_query = "SELECT * FROM social_posts"
    posts_df = pd.read_sql_query(posts_query, conn)
    conn.close()

    print(f"Found {len(posts_df)} posts in database.")

    if len(posts_df) == 0:
        print("No posts found. Please run the scrapers first.")
        return

    # Convert to format expected by analyzer
    posts_data = posts_df.to_dict('records')

    # Analyze trends
    print("\nAnalyzing social media trends...")
    trend_scores = analyzer.analyze_social_posts(posts_data)

    # Print top trends
    print("\nTop Fashion Trends:")
    print("-" * 30)
    for trend, score in sorted(trend_scores.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{trend}: {score:.2f}")

    # Generate trend report
    report = analyzer.generate_trend_report(posts_data)

    print("\nTrend Report:")
    print("-" * 30)
    print(f"Date: {report['date']}")
    print(f"Posts Analyzed: {report['total_posts_analyzed']}")
    print("\nTop Trends:")
    for trend, score in report['top_trends'][:10]:
        print(f"  {trend}: {score:.2f}")

    print("\nCategorized Trends:")
    for category, trends in report['categories'].items():
        if trends:  # Only show categories with trends
            print(f"\n{category.upper()}:")
            for trend, score in trends[:3]:  # Show top 3 per category
                print(f"  {trend}: {score:.2f}")

    # Save trend data to database
    print("\nSaving trend data to database...")
    conn = db.create_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

    for trend, score in trend_scores.items():
        insert_sql = """
        INSERT INTO trend_history (trend_name, score, platform, date_recorded)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(insert_sql, (trend, score, 'instagram', today))

    conn.commit()
    conn.close()

    # Create visualizations
    print("\nCreating visualizations...")
    create_trend_visualizations(trend_scores, report)

    print("\nAnalysis complete!")


def create_trend_visualizations(trend_scores, report):
    """Create visualizations for trend analysis."""
    # Create directory for visualizations
    viz_dir = os.path.join(project_root, 'data', 'visualizations')
    os.makedirs(viz_dir, exist_ok=True)

    # 1. Bar chart of top trends
    plt.figure(figsize=(12, 8))
    trends = sorted(trend_scores.items(), key=lambda x: x[1], reverse=True)[:10]

    x = [t[0] for t in trends]
    y = [t[1] for t in trends]

    bars = plt.bar(x, y, color=sns.color_palette("viridis", len(trends)))
    plt.xticks(rotation=45, ha='right')
    plt.title('Top Fashion Trends by Score', fontsize=16)
    plt.xlabel('Trend', fontsize=14)
    plt.ylabel('Score', fontsize=14)
    plt.tight_layout()

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                 f'{height:.2f}', ha='center', va='bottom', fontsize=10)

    plt.savefig(os.path.join(viz_dir, 'top_trends.png'))
    plt.close()

    # 2. Pie chart of trend categories
    category_scores = {}
    for category, trends in report['categories'].items():
        if trends:
            category_scores[category] = sum([score for _, score in trends])

    if category_scores:
        plt.figure(figsize=(10, 8))
        plt.pie(
            category_scores.values(),
            labels=category_scores.keys(),
            autopct='%1.1f%%',
            colors=sns.color_palette("viridis", len(category_scores))
        )
        plt.title('Fashion Trends by Category', fontsize=16)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, 'trend_categories.png'))
        plt.close()

    print(f"Visualizations saved to {viz_dir}")


if __name__ == "__main__":
    analyze_social_trends()