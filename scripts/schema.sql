CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    country VARCHAR(80) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS refunds (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    amount NUMERIC(12, 2) NOT NULL,
    reason VARCHAR(120) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics_summary (
    id INTEGER PRIMARY KEY,
    total_orders INTEGER NOT NULL DEFAULT 0,
    total_revenue NUMERIC(14, 2) NOT NULL DEFAULT 0,
    total_refunds NUMERIC(14, 2) NOT NULL DEFAULT 0,
    net_revenue NUMERIC(14, 2) NOT NULL DEFAULT 0,
    average_order_value NUMERIC(14, 2) NOT NULL DEFAULT 0,
    repeat_customer_revenue NUMERIC(14, 2) NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS revenue_trends (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    revenue NUMERIC(14, 2) NOT NULL DEFAULT 0,
    refunds NUMERIC(14, 2) NOT NULL DEFAULT 0,
    net_revenue NUMERIC(14, 2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS top_customers (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    customer_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL,
    total_spend NUMERIC(14, 2) NOT NULL,
    order_count INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

CREATE INDEX IF NOT EXISTS idx_refunds_order_id ON refunds(order_id);
CREATE INDEX IF NOT EXISTS idx_refunds_customer_id ON refunds(customer_id);
CREATE INDEX IF NOT EXISTS idx_refunds_created_at ON refunds(created_at);

CREATE INDEX IF NOT EXISTS idx_revenue_trends_date ON revenue_trends(date);
CREATE INDEX IF NOT EXISTS idx_top_customers_spend ON top_customers(total_spend DESC);