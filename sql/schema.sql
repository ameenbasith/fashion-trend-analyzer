-- SQLite Schema for Fashion Trend Analyzer

-- Brands table
CREATE TABLE IF NOT EXISTS brands (
    brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL,
    brand_category TEXT,
    website TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,
    parent_category_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    brand_id INTEGER,
    category_id INTEGER,
    description TEXT,
    material TEXT,
    gender TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES brands(brand_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Price history table
CREATE TABLE IF NOT EXISTS price_history (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    price DECIMAL(10, 2) NOT NULL,
    sale_price DECIMAL(10, 2),
    currency TEXT DEFAULT 'USD',
    date_recorded DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Popularity metrics table
CREATE TABLE IF NOT EXISTS popularity_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    reviews_count INTEGER DEFAULT 0,
    avg_rating DECIMAL(3, 2),
    date_recorded DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_product_brand ON products(brand_id);
CREATE INDEX IF NOT EXISTS idx_product_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_price_product ON price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_price_date ON price_history(date_recorded);
CREATE INDEX IF NOT EXISTS idx_popularity_product ON popularity_metrics(product_id);
CREATE INDEX IF NOT EXISTS idx_popularity_date ON popularity_metrics(date_recorded);