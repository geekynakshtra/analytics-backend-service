# API Documentation

## Health

### GET /health

Returns service health.

## Admin APIs

### POST /admin/generate?seed=42

Generates deterministic test data.

Generated data:

- 100,000 customers
- 1,000,000 orders
- 200,000 refunds

### POST /admin/ingest?page_size=5000

Fetches records from mock paginated APIs and upserts them into PostgreSQL.

### POST /admin/refresh-analytics

Refreshes pre-aggregated analytics tables.

## Mock APIs

### GET /mock/customers?page=1&page_size=1000

Returns paginated customers.

### GET /mock/orders?page=1&page_size=1000

Returns paginated orders.

### GET /mock/refunds?page=1&page_size=1000

Returns paginated refunds.

## Analytics APIs

### GET /analytics/summary

Returns:

- total_orders
- total_revenue
- total_refunds
- net_revenue
- average_order_value
- repeat_customer_revenue

### GET /analytics/revenue-trends?limit=30

Returns daily revenue, refunds, and net revenue trends.

### GET /analytics/top-customers?limit=10

Returns top customers by total completed order spend.