# Fashion Trend Analyzer

A data science project that analyzes and predicts fashion trends using machine learning.

## Project Overview

The Fashion Trend Analyzer is a comprehensive system that collects fashion trend data, analyzes current popularity patterns, and predicts future trend movements using machine learning. The project demonstrates expertise in data collection, database management, trend analysis, visualization, and predictive modeling.

## Key Features

- **Data Collection System**: Collects fashion product data and social media trend information from multiple sources
- **SQLite Database**: Stores structured data on products, brands, trends, and social media metrics
- **Trend Analysis Engine**: Identifies popular fashion styles, categories, and brands based on engagement metrics
- **Machine Learning Prediction**: Uses Random Forest Regression to forecast trend movements over time
- **Interactive Visualization**: Creates charts and dashboards to visualize trend data

## Technologies Used

- **Python**: Core programming language
- **SQLite**: Database management
- **Pandas/NumPy**: Data manipulation and analysis
- **Scikit-learn**: Machine learning models
- **Matplotlib/Seaborn**: Data visualization
- **Dash**: Interactive web dashboards

## Key Findings

The trend analysis and prediction model revealed several significant fashion insights:

1. **Dominant Aesthetic Categories**: 
   - Y2K fashion (#y2kfashion) continues to show strong growth potential
   - Baggy/oversized styles consistently rank among the most popular trends
   - Sustainability-focused fashion (#sustainablestyle) shows increased engagement

2. **Brand Performance**:
   - Athleisure brands (Nike, Adidas) maintain strong popularity
   - Workwear brands (Carhartt, Dickies) demonstrate significant growth potential
   - Fast fashion (Zara, H&M) continues to dominate despite sustainability concerns

3. **Emerging Trends**:
   - "Gorpcore" (outdoor/technical clothing worn as fashion) shows rapid growth
   - Gender-neutral fashion is increasingly mainstream
   - "Dopamine dressing" (wearing bright colors for mood enhancement) is gaining traction

4. **Declining Trends**:
   - Cuban link jewelry shows signs of declining popularity
   - Some aesthetic concepts like "dark academia" may be stabilizing after initial growth

## Project Structure

- `data/`: Raw and processed data files
- `src/`: Source code for all project components
  - `data_collection/`: Scraping and data generation modules
  - `database/`: Database setup and management
  - `analysis/`: Trend analysis algorithms
  - `visualization/`: Visualization tools and dashboards
- `models/`: Saved machine learning models
- `sql/`: SQL scripts for database setup
- `data/predictions/`: Generated trend forecasts

## Future Improvements

- Implement more sophisticated data collection from fashion retail sites
- Refine the prediction model for better trend differentiation
- Add sentiment analysis for trend perception
- Create a full-featured web application interface

## Screenshots

[Add screenshots of visualizations and dashboards here]

## Installation and Usage

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Set up the database: `python src/database/database_setup.py`
4. Generate sample data: `python src/data_collection/enhanced_data_generator.py`
5. Run the trend analyzer: `python src/analysis/trend_analyzer.py`
6. Generate predictions: `python src/analysis/trend_predictor.py`
7. Launch the dashboard: `python src/visualization/trend_dashboard.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.