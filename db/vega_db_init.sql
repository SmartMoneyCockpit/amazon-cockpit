-- Core tables
CREATE TABLE IF NOT EXISTS settings (
  id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT, updated_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY, asin TEXT UNIQUE, sku TEXT, title TEXT, brand TEXT, category TEXT,
  price NUMERIC, cost NUMERIC, inventory INT, reviews INT, stars NUMERIC, weight_kg NUMERIC,
  size TEXT, restricted_notes TEXT, updated_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS ads_campaigns (
  id SERIAL PRIMARY KEY, campaign_id TEXT, name TEXT, impressions INT, clicks INT,
  spend NUMERIC, orders INT, acos NUMERIC, roas NUMERIC, created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS compliance (
  id SERIAL PRIMARY KEY, asin TEXT, doc_type TEXT, issuer TEXT, issued_on DATE,
  expires_on DATE, link TEXT, notes TEXT
);
CREATE TABLE IF NOT EXISTS product_research (
  id SERIAL PRIMARY KEY, asin TEXT, competitor_title TEXT, price NUMERIC, reviews INT,
  stars NUMERIC, size TEXT, restricted_notes TEXT, opportunity_score NUMERIC,
  updated_at TIMESTAMP DEFAULT NOW()
);
