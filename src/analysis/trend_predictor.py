# src/analysis/trend_predictor.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import joblib

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.database_setup import DatabaseManager


class FashionTrendPredictor:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.models = {}
        self.features = {}

        # Create directory for models
        self.models_dir = os.path.join(project_root, 'models')
        os.makedirs(self.models_dir, exist_ok=True)

    def prepare_data(self, min_days=7, prediction_days=7):
        """Prepare trend data for modeling."""
        conn = self.db_manager.create_connection()

        # Get trend history
        trend_df = pd.read_sql_query("SELECT * FROM trend_history", conn)
        conn.close()

        if trend_df.empty:
            print("No trend data available for modeling.")
            return None

        # Convert date to datetime
        trend_df['date_recorded'] = pd.to_datetime(trend_df['date_recorded'])

        # Get unique trends
        unique_trends = trend_df['trend_name'].unique()

        # Prepare training data for each trend
        X_train_dict = {}
        y_train_dict = {}

        for trend in unique_trends:
            # Get data for this trend
            trend_data = trend_df[trend_df['trend_name'] == trend].sort_values('date_recorded')

            # Skip if not enough data points
            if len(trend_data) < min_days:
                continue

            # Create time-based features
            trend_data['day_of_week'] = trend_data['date_recorded'].dt.dayofweek
            trend_data['day_of_month'] = trend_data['date_recorded'].dt.day
            trend_data['month'] = trend_data['date_recorded'].dt.month

            # Create lag features
            for lag in range(1, min(5, len(trend_data))):
                trend_data[f'score_lag_{lag}'] = trend_data['score'].shift(lag)

            # Drop rows with NaN from lag features
            trend_data = trend_data.dropna()

            # Skip if not enough data after creating features
            if len(trend_data) < 5:
                continue

            # Features and target
            feature_cols = ['day_of_week', 'day_of_month', 'month'] + [f'score_lag_{lag}' for lag in
                                                                       range(1, min(5, len(trend_data)))]
            X = trend_data[feature_cols].values
            y = trend_data['score'].values

            X_train_dict[trend] = X
            y_train_dict[trend] = y
            self.features[trend] = feature_cols

        return X_train_dict, y_train_dict

    def train_models(self):
        """Train prediction models for each trend."""
        # Prepare data
        train_data = self.prepare_data()

        if not train_data:
            print("Insufficient data for training models.")
            return False

        X_train_dict, y_train_dict = train_data

        # Train a model for each trend
        for trend in X_train_dict.keys():
            # Use Random Forest for prediction
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_dict[trend], y_train_dict[trend])

            # Save the model
            self.models[trend] = model
            model_path = os.path.join(self.models_dir, f'{trend.replace("/", "_").replace(":", "_")}_model.pkl')
            joblib.dump(model, model_path)

            print(f"Trained and saved model for trend: {trend}")

        return True

    def predict_future_trends(self, days=7):
        """Predict trend scores for the next few days."""
        conn = self.db_manager.create_connection()

        # Get latest trend data
        trend_df = pd.read_sql_query("SELECT * FROM trend_history", conn)
        conn.close()

        if trend_df.empty:
            print("No trend data available for prediction.")
            return None

        # Convert date to datetime
        trend_df['date_recorded'] = pd.to_datetime(trend_df['date_recorded'])

        # Prepare predictions dataframe
        predictions = []

        for trend, model in self.models.items():
            # Get data for this trend
            trend_data = trend_df[trend_df['trend_name'] == trend].sort_values('date_recorded')

            # Skip if no data for this trend
            if len(trend_data) == 0:
                continue

            # Get feature columns
            feature_cols = self.features[trend]

            # Get the latest date
            latest_date = trend_data['date_recorded'].max()

            # Make predictions for future days
            for day in range(1, days + 1):
                future_date = latest_date + timedelta(days=day)

                # Create features for prediction
                future_features = []

                # Time features
                future_features.extend([
                    future_date.dayofweek,  # day_of_week
                    future_date.day,  # day_of_month
                    future_date.month  # month
                ])

                # Lag features
                recent_scores = trend_data.sort_values('date_recorded', ascending=False)['score'].values
                for lag in range(min(4, len(recent_scores))):
                    future_features.append(recent_scores[lag])

                # Pad with zeros if not enough lag features
                while len(future_features) < len(feature_cols):
                    future_features.append(0)

                # Make prediction
                predicted_score = model.predict([future_features])[0]

                # Add to predictions
                predictions.append({
                    'trend_name': trend,
                    'predicted_score': max(0, predicted_score),  # Ensure non-negative
                    'date': future_date.strftime('%Y-%m-%d'),
                    'days_ahead': day
                })

        return pd.DataFrame(predictions)

    def visualize_predictions(self, predictions_df):
        """Visualize trend predictions."""
        if predictions_df is None or predictions_df.empty:
            print("No predictions to visualize.")
            return

        # Create visualization directory
        viz_dir = os.path.join(project_root, 'data', 'predictions')
        os.makedirs(viz_dir, exist_ok=True)

        # Get top predicted trends
        top_trends = (
            predictions_df[predictions_df['days_ahead'] == predictions_df['days_ahead'].max()]
            .sort_values('predicted_score', ascending=False)
            .head(10)['trend_name'].unique()
        )

        # Plot predictions for top trends
        plt.figure(figsize=(14, 10))

        for trend in top_trends:
            trend_data = predictions_df[predictions_df['trend_name'] == trend]
            plt.plot(trend_data['days_ahead'], trend_data['predicted_score'], marker='o', linewidth=2, label=trend)

        plt.title('Fashion Trend Prediction', fontsize=16)
        plt.xlabel('Days in Future', fontsize=14)
        plt.ylabel('Predicted Score', fontsize=14)
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.savefig(os.path.join(viz_dir, 'trend_predictions.png'))
        plt.close()

        # Save predictions to CSV
        predictions_df.to_csv(os.path.join(viz_dir, 'fashion_trend_predictions.csv'), index=False)

        print(f"Visualizations and predictions saved to {viz_dir}")

        return os.path.join(viz_dir, 'trend_predictions.png')


if __name__ == "__main__":
    db = DatabaseManager()
    predictor = FashionTrendPredictor(db)

    print("Training trend prediction models...")
    success = predictor.train_models()

    if success:
        print("\nPredicting future trends...")
        predictions = predictor.predict_future_trends(days=14)

        if predictions is not None:
            print(f"Generated {len(predictions)} predictions.")

            print("\nTop predicted trends:")
            top_future = predictions[predictions['days_ahead'] == 14].sort_values('predicted_score',
                                                                                  ascending=False).head(10)
            for i, (_, row) in enumerate(top_future.iterrows(), 1):
                print(f"{i}. {row['trend_name']} - Score: {row['predicted_score']:.2f}")

            print("\nCreating visualizations...")
            viz_path = predictor.visualize_predictions(predictions)
            print(f"Visualization saved to: {viz_path}")
        else:
            print("No predictions could be generated.")
    else:
        print("Model training failed.")