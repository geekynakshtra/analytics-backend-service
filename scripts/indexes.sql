CREATE INDEX IF NOT EXISTS idx_orders_status_amount ON orders(status, amount);
CREATE INDEX IF NOT EXISTS idx_orders_customer_status ON orders(customer_id, status);
CREATE INDEX IF NOT EXISTS idx_orders_created_status ON orders(created_at, status);

CREATE INDEX IF NOT EXISTS idx_refunds_created_amount ON refunds(created_at, amount);
CREATE INDEX IF NOT EXISTS idx_refunds_customer_amount ON refunds(customer_id, amount);

CREATE INDEX IF NOT EXISTS idx_analytics_summary_id ON analytics_summary(id);
CREATE INDEX IF NOT EXISTS idx_revenue_trends_date_desc ON revenue_trends(date DESC);
CREATE INDEX IF NOT EXISTS idx_top_customers_total_spend_desc ON top_customers(total_spend DESC);
