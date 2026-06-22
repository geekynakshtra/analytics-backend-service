# Analytics Backend Service

A high-performance backend service built with **Python, FastAPI, and PostgreSQL**.

This project generates large reproducible datasets, exposes paginated mock APIs, ingests data from those APIs into internal warehouse tables, and provides analytics endpoints with response times consistently below **2 seconds** using indexing and pre-aggregation.

---

## Problem Statement

Build a backend service that:

* Generates large datasets:

  * 100,000 customers
  * 1,000,000 orders
  * 200,000 refunds
* Exposes mock APIs for customers, orders, and refunds
* Supports pagination
* Ingests data from mock APIs into PostgreSQL
* Provides analytics APIs
* Maintains analytics response time below 2 seconds
* Includes load testing and documentation

---

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Pydantic Settings
* HTTPX
* Faker
* Docker
* Docker Compose
* Locust

---

## Dataset

The service generates deterministic data using a reproducible seed.

| Dataset   |     Count |
| --------- | --------: |
| Customers |   100,000 |
| Orders    | 1,000,000 |
| Refunds   |   200,000 |

Default seed:

```bash
42
```

Data generation endpoint:

```http
POST /admin/generate?seed=42
```

---

## Main Features

### 1. Reproducible Data Generation

The project uses Faker and Python random seeding to generate the same dataset repeatedly.

Generated entities:

* Customers
* Orders
* Refunds

### 2. Paginated Mock APIs

Mock APIs simulate external APIs.

```http
GET /mock/customers?page=1&page_size=1000
GET /mock/orders?page=1&page_size=1000
GET /mock/refunds?page=1&page_size=1000
```

### 3. Ingestion Service

The ingestion service pulls data from mock APIs page by page and stores it in PostgreSQL using upsert logic.

```http
POST /admin/ingest?page_size=10000
```

### 4. Analytics APIs

Analytics endpoints provide:

* Total Orders
* Total Revenue
* Total Refunds
* Net Revenue
* Average Order Value
* Repeat Customer Revenue
* Revenue Trends
* Top Customers by Spend

```http
GET /analytics/summary
GET /analytics/revenue-trends?limit=30
GET /analytics/top-customers?limit=10
```

### 5. Performance Optimization

Analytics are pre-aggregated into smaller tables so API requests do not scan millions of rows each time.

---

## Improved Data Architecture

The project separates external mock API data from internal ingested warehouse data.

```text
Mock Source Tables
mock_customers
mock_orders
mock_refunds
        ↓
Paginated Mock APIs
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
Pre-Aggregated Analytics Tables
analytics_summary
revenue_trends
top_customers
        ↓
Fast Analytics APIs
GET /analytics/summary
GET /analytics/revenue-trends
GET /analytics/top-customers
```

This design makes the ingestion pipeline realistic. The mock tables simulate external APIs, while the internal warehouse tables represent data after ingestion.

---

## Backend Architecture

The service follows a layered backend architecture.

```text
FastAPI Routers
    ↓
Service Layer
    ↓
SQLAlchemy ORM / Raw SQL
    ↓
PostgreSQL
```

### Layer Responsibilities

| Layer          | Responsibility                                   | Files                                       |
| -------------- | ------------------------------------------------ | ------------------------------------------- |
| API Layer      | Defines HTTP endpoints                           | `app/api/*.py`                              |
| Service Layer  | Business logic, generation, ingestion, analytics | `app/services/*.py`                         |
| Database Layer | DB connection and session handling               | `app/db/database.py`                        |
| Model Layer    | SQLAlchemy table models                          | `app/models/tables.py`                      |
| SQL Scripts    | Schema and indexes                               | `scripts/schema.sql`, `scripts/indexes.sql` |
| Load Testing   | Concurrent API testing                           | `scripts/locustfile.py`                     |

---

## Project Structure

```text
analytics-backend-service/
│
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── admin.py
│   │   ├── analytics.py
│   │   └── mock_api.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   └── tables.py
│   └── services/
│       ├── analytics_service.py
│       ├── generator.py
│       └── ingestion.py
│
├── scripts/
│   ├── schema.sql
│   ├── indexes.sql
│   └── locustfile.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Database Design

The database is divided into three main groups.

### 1. Mock Source Tables

These tables simulate data coming from external APIs.

| Table            | Purpose              |
| ---------------- | -------------------- |
| `mock_customers` | Source customer data |
| `mock_orders`    | Source order data    |
| `mock_refunds`   | Source refund data   |

### 2. Internal Warehouse Tables

These tables store ingested data.

| Table       | Purpose                   |
| ----------- | ------------------------- |
| `customers` | Ingested customer records |
| `orders`    | Ingested order records    |
| `refunds`   | Ingested refund records   |

### 3. Analytics Tables

These tables store precomputed analytics.

| Table               | Purpose                                |
| ------------------- | -------------------------------------- |
| `analytics_summary` | Summary metrics                        |
| `revenue_trends`    | Daily revenue/refund trends            |
| `top_customers`     | Top customers by completed order spend |

---

## Database Indexing

Indexes are added for high-volume lookup, filtering, grouping, and sorting.

Examples:

```sql
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

CREATE INDEX IF NOT EXISTS idx_refunds_order_id ON refunds(order_id);
CREATE INDEX IF NOT EXISTS idx_refunds_customer_id ON refunds(customer_id);
CREATE INDEX IF NOT EXISTS idx_refunds_created_at ON refunds(created_at);

CREATE INDEX IF NOT EXISTS idx_revenue_trends_date ON revenue_trends(date);
CREATE INDEX IF NOT EXISTS idx_top_customers_spend ON top_customers(total_spend DESC);
```

Additional performance indexes are included in:

```text
scripts/indexes.sql
```

---

## API Endpoints

### Health

| Method | Endpoint  | Description           |
| ------ | --------- | --------------------- |
| GET    | `/health` | Checks service health |

### Admin APIs

| Method | Endpoint                        | Description                                      |
| ------ | ------------------------------- | ------------------------------------------------ |
| POST   | `/admin/generate?seed=42`       | Generates deterministic mock source data         |
| POST   | `/admin/ingest?page_size=10000` | Ingests data from mock APIs into internal tables |
| POST   | `/admin/refresh-analytics`      | Refreshes pre-aggregated analytics tables        |

### Mock APIs

| Method | Endpoint                                | Description                 |
| ------ | --------------------------------------- | --------------------------- |
| GET    | `/mock/customers?page=1&page_size=1000` | Returns paginated customers |
| GET    | `/mock/orders?page=1&page_size=1000`    | Returns paginated orders    |
| GET    | `/mock/refunds?page=1&page_size=1000`   | Returns paginated refunds   |

### Analytics APIs

| Method | Endpoint                             | Description                |
| ------ | ------------------------------------ | -------------------------- |
| GET    | `/analytics/summary`                 | Returns summary metrics    |
| GET    | `/analytics/revenue-trends?limit=30` | Returns revenue trend data |
| GET    | `/analytics/top-customers?limit=10`  | Returns top customers      |

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd analytics-backend-service
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL

```bash
docker compose up -d postgres
```

Check container:

```bash
docker ps
```

Expected container name:

```text
analytics_postgres
```

### 5. Create Tables

```bash
docker cp scripts/schema.sql analytics_postgres:/schema.sql
docker exec -it analytics_postgres psql -U postgres -d analytics_db -f /schema.sql
```

### 6. Apply Indexes

```bash
docker cp scripts/indexes.sql analytics_postgres:/indexes.sql
docker exec -it analytics_postgres psql -U postgres -d analytics_db -f /indexes.sql
```

### 7. Start FastAPI

```bash
uvicorn app.main:app --reload
```

Server URL:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Running the Full Pipeline

### Step 1: Generate Mock Source Data

```bash
curl -X POST "http://127.0.0.1:8000/admin/generate?seed=42"
```

Expected response:

```json
{
  "message": "Data generated successfully",
  "seed": 42,
  "customers": 100000,
  "orders": 1000000,
  "refunds": 200000
}
```

This fills:

```text
mock_customers
mock_orders
mock_refunds
```

---

### Step 2: Verify Mock API

```bash
curl "http://127.0.0.1:8000/mock/customers?page=1&page_size=5"
```

Expected response shape:

```json
{
  "page": 1,
  "page_size": 5,
  "total": 100000,
  "total_pages": 20000,
  "data": []
}
```

The `data` field will contain 5 customer records.

---

### Step 3: Run Ingestion

```bash
curl -X POST "http://127.0.0.1:8000/admin/ingest?page_size=10000"
```

Expected response:

```json
{
  "message": "Ingestion completed successfully",
  "page_size": 10000,
  "ingested": {
    "customers": 100000,
    "orders": 1000000,
    "refunds": 200000
  }
}
```

This fills:

```text
customers
orders
refunds
```

---

### Step 4: Refresh Analytics

```bash
curl -X POST "http://127.0.0.1:8000/admin/refresh-analytics"
```

Expected response:

```json
{
  "message": "Analytics refreshed successfully"
}
```

This fills:

```text
analytics_summary
revenue_trends
top_customers
```

---

### Step 5: Test Analytics APIs

Summary:

```bash
curl "http://127.0.0.1:8000/analytics/summary"
```

Revenue trends:

```bash
curl "http://127.0.0.1:8000/analytics/revenue-trends?limit=5"
```

Top customers:

```bash
curl "http://127.0.0.1:8000/analytics/top-customers?limit=5"
```

---

## Database Verification Commands

Open PostgreSQL shell:

```bash
docker exec -it analytics_postgres psql -U postgres -d analytics_db
```

Show tables:

```sql
\dt
```

Check mock source table counts:

```sql
SELECT COUNT(*) FROM mock_customers;
SELECT COUNT(*) FROM mock_orders;
SELECT COUNT(*) FROM mock_refunds;
```

Check internal warehouse table counts:

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM refunds;
```

Expected after full pipeline:

| Table            |     Count |
| ---------------- | --------: |
| `mock_customers` |   100,000 |
| `mock_orders`    | 1,000,000 |
| `mock_refunds`   |   200,000 |
| `customers`      |   100,000 |
| `orders`         | 1,000,000 |
| `refunds`        |   200,000 |

Exit PostgreSQL:

```sql
\q
```

---

## Example Analytics Response

### `GET /analytics/summary`

Response shape:

```json
{
  "total_orders": 1000000,
  "total_revenue": 8040000000.0,
  "total_refunds": 501000000.0,
  "net_revenue": 7539000000.0,
  "average_order_value": 10050.0,
  "repeat_customer_revenue": 8030000000.0,
  "updated_at": "2026-06-22T10:00:00"
}
```

Values may differ slightly depending on seed and generated amounts.

---

## Load Testing

Load testing is done using Locust.

### Run Load Test

```bash
locust -f scripts/locustfile.py \
  --host=http://127.0.0.1:8000 \
  --users 50 \
  --spawn-rate 10 \
  --run-time 1m \
  --headless
```

### Tested Endpoints

* `GET /analytics/summary`
* `GET /analytics/revenue-trends?limit=30`
* `GET /analytics/top-customers?limit=10`
* `GET /health`

### Load Test Results

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

The analytics endpoints stayed below the required **2-second response time** during load testing.

---

## Performance Optimization Decisions

### 1. Pre-Aggregation

Analytics are not calculated directly from the large raw tables during every request.

Instead:

```http
POST /admin/refresh-analytics
```

calculates analytics once and stores results in:

```text
analytics_summary
revenue_trends
top_customers
```

This makes read APIs extremely fast.

### 2. Bulk Insert

Large datasets are inserted in batches using SQLAlchemy bulk insert mappings.

This reduces transaction overhead and improves data generation performance.

### 3. Pagination

Mock APIs use pagination to avoid returning huge datasets in one response.

Ingestion also consumes records page by page.

### 4. Upsert During Ingestion

The ingestion service uses PostgreSQL upsert logic.

This prevents duplicate data when ingestion is run multiple times.

### 5. Indexing

Indexes are added on frequently queried and joined columns.

This improves analytics refresh, sorting, filtering, and lookup performance.

### 6. Connection Pooling

SQLAlchemy engine pooling is configured to reuse database connections efficiently.

---

## Scalability Considerations

The current design can scale further with:

* Redis caching for analytics responses
* Celery background jobs for ingestion and analytics refresh
* PostgreSQL partitioning for large orders/refunds tables
* Materialized views for analytics
* Read replicas for analytics reads
* Separate worker service for ingestion
* API rate limiting for mock/external APIs
* Batch checkpoints to resume ingestion after failure

These are not required for this assignment but are natural next steps for production.

---

## Docker Usage

Start full stack:

```bash
docker compose up --build
```

Run only PostgreSQL:

```bash
docker compose up -d postgres
```

Stop services:

```bash
docker compose down
```

Reset database volume:

```bash
docker compose down -v
```

---

## Environment Variables

The default local database URL is:

```text
postgresql://postgres:postgres@localhost:5432/analytics_db
```

Inside Docker Compose, the API uses:

```text
postgresql://postgres:postgres@postgres:5432/analytics_db
```

Example `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/analytics_db
APP_NAME=Analytics Backend Service
```

---

## Code Quality Notes

The project keeps responsibilities separated:

* API route files only define endpoints.
* Service files contain business logic.
* Database configuration is centralized.
* SQL schema and indexes are stored in scripts.
* Analytics logic is isolated in a dedicated service.
* Load testing is included separately.
* `.venv` and cache files are ignored through `.gitignore`.

---

## Evaluation Criteria Coverage

| Criteria                 | How This Project Covers It                                                                |
| ------------------------ | ----------------------------------------------------------------------------------------- |
| Backend Architecture     | Layered FastAPI architecture with API, service, DB, and model layers                      |
| Database Design          | Separate mock source tables, internal warehouse tables, and analytics tables              |
| API Design               | Clear admin, mock, analytics, and health endpoints                                        |
| Performance Optimization | Pre-aggregation, indexing, bulk inserts, upserts, connection pooling                      |
| Scalability              | Pagination, batch processing, upsert ingestion, Docker setup, future Redis/Celery support |
| Code Quality             | Modular structure, clear naming, separate services, documentation, load test              |

---

## GitHub Submission Checklist

* [x] FastAPI backend
* [x] PostgreSQL database
* [x] Reproducible seed-based data generation
* [x] 100,000 customers
* [x] 1,000,000 orders
* [x] 200,000 refunds
* [x] Paginated mock APIs
* [x] Ingestion service
* [x] Separate mock source and internal warehouse tables
* [x] Analytics endpoints
* [x] Pre-aggregated analytics tables
* [x] PostgreSQL indexes
* [x] Docker setup
* [x] Locust load test
* [x] Setup instructions
* [x] API documentation
* [x] Architecture explanation
* [x] Load test results

---

## Author

Nakshatra Tyagi
