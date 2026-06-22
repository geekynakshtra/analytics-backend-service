# Architecture and Optimization Decisions

## 1. Overview

This project is a high-volume analytics backend built using **FastAPI** and **PostgreSQL**.

It supports:

* Reproducible generation of 1.3 million records
* Paginated mock APIs
* Ingestion from mock APIs into PostgreSQL
* Analytics APIs with response time below 2 seconds
* Load testing with concurrent requests

---

## 2. High-Level Architecture

```text
Client / Load Test
        ↓
FastAPI Application
        ↓
API Routers
        ↓
Service Layer
        ↓
SQLAlchemy ORM / Raw SQL
        ↓
PostgreSQL
```

---

## 3. Application Layers

### API Layer

The API layer defines HTTP endpoints and request parameters.

Files:

```text
app/api/admin.py
app/api/mock_api.py
app/api/analytics.py
```

Responsibilities:

* Expose admin endpoints
* Expose mock paginated APIs
* Expose analytics APIs
* Validate query parameters
* Return JSON responses

---

### Service Layer

The service layer contains business logic.

Files:

```text
app/services/generator.py
app/services/ingestion.py
app/services/analytics_service.py
```

Responsibilities:

* Generate large datasets
* Pull data from paginated APIs
* Upsert ingested records
* Refresh analytics tables
* Execute optimized SQL aggregation queries

---

### Database Layer

The database layer manages PostgreSQL connection and sessions.

Files:

```text
app/db/database.py
app/models/tables.py
scripts/schema.sql
scripts/indexes.sql
```

Responsibilities:

* Create SQLAlchemy engine
* Manage DB sessions
* Define ORM models
* Create database schema
* Apply indexes

---

## 4. Improved Data Flow

The project uses separate source and destination tables.

```text
Mock Source Tables
mock_customers
mock_orders
mock_refunds
        ↓
Mock APIs
GET /mock/customers
GET /mock/orders
GET /mock/refunds
        ↓
Ingestion Service
POST /admin/ingest
        ↓
Internal Warehouse Tables
customers
orders
refunds
        ↓
Analytics Refresh
POST /admin/refresh-analytics
        ↓
Pre-Aggregated Tables
analytics_summary
revenue_trends
top_customers
        ↓
Analytics APIs
GET /analytics/summary
GET /analytics/revenue-trends
GET /analytics/top-customers
```

This separation makes the architecture closer to a real production ingestion pipeline.

---

## 5. Database Design

### Mock Source Tables

These tables simulate external API data.

| Table            | Description             |
| ---------------- | ----------------------- |
| `mock_customers` | Source customer records |
| `mock_orders`    | Source order records    |
| `mock_refunds`   | Source refund records   |

### Internal Warehouse Tables

These tables store ingested data.

| Table       | Description        |
| ----------- | ------------------ |
| `customers` | Ingested customers |
| `orders`    | Ingested orders    |
| `refunds`   | Ingested refunds   |

### Analytics Tables

These tables store precomputed analytics.

| Table               | Description                             |
| ------------------- | --------------------------------------- |
| `analytics_summary` | Overall business metrics                |
| `revenue_trends`    | Daily revenue/refund/net revenue trends |
| `top_customers`     | Top customers by spend                  |

---

## 6. API Design

The APIs are grouped by purpose.

### Admin APIs

```text
POST /admin/generate
POST /admin/ingest
POST /admin/refresh-analytics
```

Admin APIs handle data generation, ingestion, and analytics refresh.

### Mock APIs

```text
GET /mock/customers
GET /mock/orders
GET /mock/refunds
```

Mock APIs simulate external paginated APIs.

### Analytics APIs

```text
GET /analytics/summary
GET /analytics/revenue-trends
GET /analytics/top-customers
```

Analytics APIs provide fast business metrics.

### Health API

```text
GET /health
```

Used for service health checks and load testing.

---

## 7. Ingestion Design

The ingestion service uses HTTP calls to consume mock APIs page by page.

Example:

```text
GET /mock/orders?page=1&page_size=10000
GET /mock/orders?page=2&page_size=10000
...
```

This demonstrates handling of paginated APIs and avoids loading all data at once.

The ingestion service uses PostgreSQL upsert logic:

```text
INSERT ... ON CONFLICT DO UPDATE
```

Benefits:

* Prevents duplicate records
* Allows ingestion to be safely rerun
* Makes the pipeline idempotent

---

## 8. Analytics Design

Analytics are calculated in a refresh step:

```text
POST /admin/refresh-analytics
```

This endpoint computes:

* Total Orders
* Total Revenue
* Total Refunds
* Net Revenue
* Average Order Value
* Repeat Customer Revenue
* Revenue Trends
* Top Customers by Spend

The results are stored in:

```text
analytics_summary
revenue_trends
top_customers
```

The read APIs then query only these small tables.

This avoids scanning 1,000,000 orders and 200,000 refunds on every analytics request.

---

## 9. Performance Optimization

### 1. Pre-Aggregation

Expensive analytics calculations are moved out of request-time analytics APIs.

Instead of calculating every metric on every request, the service refreshes analytics once and serves fast reads from precomputed tables.

### 2. Indexing

Indexes are added on high-use columns:

```text
orders.customer_id
orders.created_at
orders.status
refunds.order_id
refunds.customer_id
refunds.created_at
revenue_trends.date
top_customers.total_spend
```

Indexes help with joins, grouping, sorting, and filtering.

### 3. Bulk Inserts

The data generator inserts records in batches.

This is much faster than inserting one row at a time.

### 4. Pagination

Mock APIs and ingestion both use pagination.

This keeps memory usage controlled and makes the service more scalable.

### 5. Upsert

Ingestion uses upsert to prevent duplicate records and support repeated ingestion runs.

### 6. Connection Pooling

SQLAlchemy engine configuration uses connection pooling for better DB connection reuse.

---

## 10. Load Test Results

Load testing was performed with Locust against the analytics endpoints.

Tested endpoints:

```text
GET /analytics/summary
GET /analytics/revenue-trends?limit=30
GET /analytics/top-customers?limit=10
GET /health
```

Results:

| Metric                  |   Result |
| ----------------------- | -------: |
| Total Requests          |   11,743 |
| Failed Requests         |        0 |
| Median Latency          |    10 ms |
| 95th Percentile Latency |    17 ms |
| 99th Percentile Latency |    25 ms |
| Average Latency         | 10.91 ms |
| Max Latency             |  1339 ms |
| Current RPS             |  1074.47 |

The analytics APIs stayed below the required 2-second response time.

---

## 11. Scalability

The current architecture supports scalability through:

* Pagination
* Batch insertion
* Idempotent ingestion
* PostgreSQL indexes
* Pre-aggregated analytics tables
* Dockerized environment
* Connection pooling

Future production improvements could include:

* Redis caching
* Celery background workers
* Scheduled analytics refresh
* PostgreSQL table partitioning
* Materialized views
* Read replicas
* Ingestion checkpoints
* API rate limiting

---

## 12. Evaluation Criteria Coverage

| Criteria                 | Implementation                                                            |
| ------------------------ | ------------------------------------------------------------------------- |
| Backend Architecture     | Layered FastAPI architecture with routers, services, DB, and models       |
| Database Design          | Separate mock source, internal warehouse, and analytics tables            |
| API Design               | Clear admin, mock, analytics, and health endpoint groups                  |
| Performance Optimization | Pre-aggregation, indexes, bulk inserts, upserts, connection pooling       |
| Scalability              | Pagination, batch ingestion, idempotent upserts, Docker support           |
| Code Quality             | Modular structure, clear file separation, documentation, load test script |

---

## 13. Summary

This backend service demonstrates a realistic data ingestion and analytics pipeline.

It generates large datasets, exposes mock APIs, ingests paginated data into PostgreSQL, refreshes precomputed analytics tables, and serves analytics responses under the required 2-second threshold.
