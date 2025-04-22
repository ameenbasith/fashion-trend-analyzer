import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
from textblob import TextBlob


class FashionTrendAnalyzer:
    def __init__(self, db_path='data/fashion_trends.db'):
        # Get the absolute path to the database
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(project_root, db_path)
        self.project_root = project_root
        self.engine = create_engine(f'sqlite:///{self.db_path}')

        # Create directories for saving plots if they don't exist
        self.ensure_directories_exist()

    def ensure_directories_exist(self):
        """Ensure that necessary directories exist."""
        directories = [
            os.path.join(self.project_root, 'data', 'plots'),
            os.path.join(self.project_root, 'data', 'reports')
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_products_df(self):
        """Get all products with their brand and category information."""
        query = """
        SELECT p.*, b.brand_name, c.category_name 
        FROM products p
        LEFT JOIN brands b ON p.brand_id = b.brand_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        """
        return pd.read_sql_query(query, self.engine)

    def get_price_history_df(self):
        """Get all price history data with product information."""
        query = """
        SELECT ph.*, p.product_name, b.brand_name, c.category_name
        FROM price_history ph
        LEFT JOIN products p ON ph.product_id = p.product_id
        LEFT JOIN brands b ON p.brand_id = b.brand_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        """
        return pd.read_sql_query(query, self.engine)

    def analyze_category_pricing(self):
        """Analyze average prices by category."""
        df = self.get_price_history_df()

        # Calculate average price by category
        category_pricing = df.groupby('category_name')['price'].agg(['mean', 'min', 'max', 'count']).reset_index()
        category_pricing.columns = ['Category', 'Average Price', 'Min Price', 'Max Price', 'Count']

        # Sort by average price
        category_pricing = category_pricing.sort_values('Average Price', ascending=False)

        return category_pricing

    def analyze_brand_pricing(self):
        """Analyze average prices by brand."""
        df = self.get_price_history_df()

        # Calculate average price by brand
        brand_pricing = df.groupby('brand_name')['price'].agg(['mean', 'min', 'max', 'count']).reset_index()
        brand_pricing.columns = ['Brand', 'Average Price', 'Min Price', 'Max Price', 'Count']

        # Sort by average price
        brand_pricing = brand_pricing.sort_values('Average Price', ascending=False)

        return brand_pricing

    def analyze_discount_patterns(self):
        """Analyze products with discounts."""
        df = self.get_price_history_df()

        # Filter products with sale prices
        discounted = df[df['sale_price'].notna()].copy()

        if len(discounted) > 0:
            # Calculate discount percentage
            discounted['discount_percentage'] = ((discounted['price'] - discounted['sale_price']) / discounted[
                'price']) * 100

            # Group by category and calculate average discount
            category_discounts = discounted.groupby('category_name')['discount_percentage'].mean().reset_index()
            category_discounts.columns = ['Category', 'Average Discount %']
            category_discounts = category_discounts.sort_values('Average Discount %', ascending=False)

            return category_discounts
        else:
            return pd.DataFrame(columns=['Category', 'Average Discount %'])

    def get_trending_items(self, days=7):
        """Identify trending items based on recent additions."""
        query = f"""
        SELECT p.product_name, b.brand_name, c.category_name, ph.price
        FROM products p
        LEFT JOIN brands b ON p.brand_id = b.brand_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN price_history ph ON p.product_id = ph.product_id
        WHERE p.created_at >= datetime('now', '-{days} days')
        """
        return pd.read_sql_query(query, self.engine)

    def generate_brand_performance_report(self):
        """Generate a comprehensive brand performance report."""
        df = self.get_price_history_df()

        # Count products per brand
        brand_products = df.groupby('brand_name')['product_id'].nunique().reset_index()
        brand_products.columns = ['Brand', 'Product Count']

        # Average price per brand
        brand_avg_price = df.groupby('brand_name')['price'].mean().reset_index()
        brand_avg_price.columns = ['Brand', 'Average Price']

        # Discount percentage per brand
        discounted = df[df['sale_price'].notna()].copy()
        if len(discounted) > 0:
            discounted['discount_percentage'] = ((discounted['price'] - discounted['sale_price']) / discounted[
                'price']) * 100
            brand_discounts = discounted.groupby('brand_name')['discount_percentage'].mean().reset_index()
            brand_discounts.columns = ['Brand', 'Average Discount %']
        else:
            brand_discounts = pd.DataFrame(columns=['Brand', 'Average Discount %'])

        # Merge all data
        report = brand_products.merge(brand_avg_price, on='Brand', how='left')
        report = report.merge(brand_discounts, on='Brand', how='left')

        return report.sort_values('Product Count', ascending=False)

    def plot_category_distribution(self):
        """Create a pie chart of category distribution."""
        df = self.get_products_df()
        category_counts = df['category_name'].value_counts()

        plt.figure(figsize=(10, 8))
        plt.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%')
        plt.title('Distribution of Products by Category')
        plt.axis('equal')
        return plt

    def plot_price_range_by_category(self):
        """Create a box plot showing price ranges by category."""
        df = self.get_price_history_df()

        plt.figure(figsize=(12, 8))
        sns.boxplot(data=df, x='category_name', y='price')
        plt.xticks(rotation=45)
        plt.title('Price Range by Category')
        plt.xlabel('Category')
        plt.ylabel('Price ($)')
        plt.tight_layout()
        return plt


# For testing
if __name__ == "__main__":
    analyzer = FashionTrendAnalyzer()

    # Test analysis functions
    print("\nCategory Pricing Analysis:")
    print(analyzer.analyze_category_pricing())

    print("\nBrand Pricing Analysis:")
    print(analyzer.analyze_brand_pricing())

    print("\nDiscount Pattern Analysis:")
    print(analyzer.analyze_discount_patterns())

    print("\nTrending Items (Last 7 days):")
    print(analyzer.get_trending_items())

    print("\nBrand Performance Report:")
    print(analyzer.generate_brand_performance_report())

    # Create and save plots
    plots_dir = os.path.join(analyzer.project_root, 'data', 'plots')

    analyzer.plot_category_distribution().savefig(os.path.join(plots_dir, 'category_distribution.png'))
    analyzer.plot_price_range_by_category().savefig(os.path.join(plots_dir, 'price_range_by_category.png'))

    plt.close('all')
    print(f"\nAnalysis complete! Plots saved to {plots_dir}")