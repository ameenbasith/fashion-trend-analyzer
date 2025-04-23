# src/visualization/trend_dashboard.py

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.database_setup import DatabaseManager

# Initialize the Dash app
app = dash.Dash(__name__, title="Fashion Trend Analyzer")

# Database connection
db = DatabaseManager()


# Get the data
def get_trend_data():
    """Get trend data from the database."""
    conn = db.create_connection()

    # Get trend history
    trend_query = "SELECT * FROM trend_history ORDER BY date_recorded DESC, score DESC"
    trend_df = pd.read_sql_query(trend_query, conn)

    # Get social posts
    posts_query = "SELECT * FROM social_posts"
    posts_df = pd.read_sql_query(posts_query, conn)

    conn.close()

    return trend_df, posts_df


# Initial data load
trend_df, posts_df = get_trend_data()

# App layout
app.layout = html.Div([
    html.H1("Fashion Trend Analyzer Dashboard", style={'textAlign': 'center', 'marginBottom': 30}),

    html.Div([
        html.Div([
            html.H2("Top Fashion Trends", style={'textAlign': 'center'}),
            dcc.Graph(id='top-trends-chart')
        ], className='six columns'),

        html.Div([
            html.H2("Trend Categories", style={'textAlign': 'center'}),
            dcc.Graph(id='trend-categories-chart')
        ], className='six columns'),
    ], className='row'),

    html.Div([
        html.H2("Social Media Posts", style={'textAlign': 'center'}),
        html.Div(id='social-posts-container')
    ], className='row', style={'marginTop': 50}),

    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # in milliseconds (1 minute)
        n_intervals=0
    )
], style={'padding': '20px'})


# Callbacks
@app.callback(
    [Output('top-trends-chart', 'figure'),
     Output('trend-categories-chart', 'figure'),
     Output('social-posts-container', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_charts(n):
    # Refresh data
    trend_df, posts_df = get_trend_data()

    # Top trends chart
    latest_date = trend_df['date_recorded'].max() if not trend_df.empty else None
    if latest_date:
        top_trends = trend_df[trend_df['date_recorded'] == latest_date].sort_values('score', ascending=False).head(10)
        fig_top = px.bar(
            top_trends,
            x='trend_name',
            y='score',
            title=f'Top 10 Fashion Trends - {latest_date}',
            labels={'trend_name': 'Trend', 'score': 'Score'}
        )
        fig_top.update_layout(xaxis_tickangle=-45)
    else:
        # Empty chart if no data
        fig_top = go.Figure()
        fig_top.update_layout(title="No trend data available")

    # Trend categories chart
    # We'll assume trends with # are hashtags and group the rest by common keywords
    if not trend_df.empty:
        # Simple categorization - in a real app, this would be more sophisticated
        categories = {
            'Hashtags': trend_df[trend_df['trend_name'].str.startswith('#')]['score'].sum(),
            'Keywords': trend_df[~trend_df['trend_name'].str.startswith('#')]['score'].sum()
        }

        fig_cat = px.pie(
            names=list(categories.keys()),
            values=list(categories.values()),
            title='Trend Categories'
        )
    else:
        # Empty chart if no data
        fig_cat = go.Figure()
        fig_cat.update_layout(title="No category data available")

    # Social posts display
    if not posts_df.empty:
        posts_display = []
        for i, row in posts_df.iterrows():
            post_card = html.Div([
                html.H4(f"Post by {row['username']}"),
                html.P(f"Caption: {row['caption']}"),
                html.Div([
                    html.Span(f"Likes: {row['likes']}"),
                    html.Span(f" | Comments: {row['comments']}"),
                    html.Span(f" | Followers: {row['followers']}")
                ]),
                html.Hr()
            ])
            posts_display.append(post_card)
    else:
        posts_display = [html.P("No social media posts available")]

    return fig_top, fig_cat, posts_display


if __name__ == '__main__':
    app.run(debug=True)  # Changed from run_server to run