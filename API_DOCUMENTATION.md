# API Documentation

Base URL:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## 1. Health API

### GET `/health`

Checks whether the backend service is running.

#### Response

```json
{
  "status": "healthy"
}
```

---

## 2. Admin APIs

Admin APIs are used for data generation, ingestion, and analytics refresh.

---

### POST `/admin/generate`

Generates deterministic mock source data using a reproducible seed.

#### Query Parameters

| Parameter | Type    | Required | Default | Description                             |
| --------- | ------- | -------: | ------: | --------------------------------------- |
| `seed`    | integer |       No |    `42` | Seed used to generate reproducible data |

#### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/admin/generate?seed=42"
```

#### Example Response

```json
{
  "message": "Data generated successfully",
  "seed": 42,
  "customers": 100000,
  "orders": 1000000,
  "refunds": 200000
}
```

#### Notes

This endpoint fills the mock source tables:

```text
mock_customers
mock_orders
mock_refunds
```

---

### POST `/admin/ingest`

Ingests data from paginated mock APIs into internal warehouse tables.

#### Query Parameters

| Parameter   | Type    | Required | Default | Description                                         |
| ----------- | ------- | -------: | ------: | --------------------------------------------------- |
| `page_size` | integer |       No |  `5000` | Number of records fetched per page during ingestion |

#### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/admin/ingest?page_size=10000"
```

#### Example Response

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

#### Notes

This endpoint reads from:

```text
GET /mock/customers
GET /mock/orders
GET /mock/refunds
```

and writes into:

```text
customers
orders
refunds
```

The ingestion service uses PostgreSQL upsert logic to avoid duplicate records.

---

### POST `/admin/refresh-analytics`

Refreshes pre-aggregated analytics tables.

#### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/admin/refresh-analytics"
```

#### Example Response

```json
{
  "message": "Analytics refreshed successfully"
}
```

#### Notes

This endpoint reads from internal warehouse tables:

```text
customers
orders
refunds
```

and refreshes:

```text
analytics_summary
revenue_trends
top_customers
```

---

## 3. Mock APIs

Mock APIs simulate external data APIs. They expose customers, orders, and refunds with pagination.

---

### GET `/mock/customers`

Returns paginated mock customer records.

#### Query Parameters

| Parameter   | Type    | Required | Default |           Limit |
| ----------- | ------- | -------: | ------: | --------------: |
| `page`      | integer |       No |     `1` |     Minimum `1` |
| `page_size` | integer |       No |  `1000` | Maximum `10000` |

#### Example Request

```bash
curl "http://127.0.0.1:8000/mock/customers?page=1&page_size=5"
```

#### Example Response Shape

```json
{
  "page": 1,
  "page_size": 5,
  "total": 100000,
  "total_pages": 20000,
  "data": [
    {
      "id": 1,
      "name": "Customer Name",
      "email": "user1@example.com",
      "country": "India",
      "created_at": "2025-01-01T10:00:00"
    }
  ]
}
```

---

### GET `/mock/orders`

Returns paginated mock order records.

#### Query Parameters

| Parameter   | Type    | Required | Default |           Limit |
| ----------- | ------- | -------: | ------: | --------------: |
| `page`      | integer |       No |     `1` |     Minimum `1` |
| `page_size` | integer |       No |  `1000` | Maximum `10000` |

#### Example Request

```bash
curl "http://127.0.0.1:8000/mock/orders?page=1&page_size=5"
```

#### Example Response Shape

```json
{
  "page": 1,
  "page_size": 5,
  "total": 1000000,
  "total_pages": 200000,
  "data": [
    {
      "id": 1,
      "customer_id": 123,
      "amount": 1500.75,
      "status": "completed",
      "created_at": "2025-01-01T10:00:00"
    }
  ]
}
```

---

### GET `/mock/refunds`

Returns paginated mock refund records.

#### Query Parameters

| Parameter   | Type    | Required | Default |           Limit |
| ----------- | ------- | -------: | ------: | --------------: |
| `page`      | integer |       No |     `1` |     Minimum `1` |
| `page_size` | integer |       No |  `1000` | Maximum `10000` |

#### Example Request

```bash
curl "http://127.0.0.1:8000/mock/refunds?page=1&page_size=5"
```

#### Example Response Shape

```json
{
  "page": 1,
  "page_size": 5,
  "total": 200000,
  "total_pages": 40000,
  "data": [
    {
      "id": 1,
      "order_id": 500,
      "customer_id": 123,
      "amount": 250.50,
      "reason": "Late delivery",
      "created_at": "2025-01-01T10:00:00"
    }
  ]
}
```

---

## 4. Analytics APIs

Analytics APIs read from pre-aggregated analytics tables, so they return responses quickly even with the full dataset.

---

### GET `/analytics/summary`

Returns overall business metrics.

#### Example Request

```bash
curl "http://127.0.0.1:8000/analytics/summary"
```

#### Response Fields

| Field                     | Description                                               |
| ------------------------- | --------------------------------------------------------- |
| `total_orders`            | Total number of orders                                    |
| `total_revenue`           | Sum of completed order amount                             |
| `total_refunds`           | Sum of refund amount                                      |
| `net_revenue`             | Total revenue minus total refunds                         |
| `average_order_value`     | Average completed order value                             |
| `repeat_customer_revenue` | Revenue from customers with more than one completed order |
| `updated_at`              | Last analytics refresh timestamp                          |

#### Example Response

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

---

### GET `/analytics/revenue-trends`

Returns daily revenue, refunds, and net revenue trends.

#### Query Parameters

| Parameter | Type    | Required | Default |          Limit |
| --------- | ------- | -------: | ------: | -------------: |
| `limit`   | integer |       No |   `365` | Maximum `1000` |

#### Example Request

```bash
curl "http://127.0.0.1:8000/analytics/revenue-trends?limit=10"
```

#### Example Response Shape

```json
[
  {
    "date": "2026-06-22",
    "revenue": 1200000.50,
    "refunds": 80000.25,
    "net_revenue": 1120000.25
  }
]
```

---

### GET `/analytics/top-customers`

Returns top customers by completed order spend.

#### Query Parameters

| Parameter | Type    | Required | Default |         Limit |
| --------- | ------- | -------: | ------: | ------------: |
| `limit`   | integer |       No |    `10` | Maximum `100` |

#### Example Request

```bash
curl "http://127.0.0.1:8000/analytics/top-customers?limit=10"
```

#### Example Response Shape

```json
[
  {
    "customer_id": 123,
    "customer_name": "Customer Name",
    "email": "user123@example.com",
    "total_spend": 250000.75,
    "order_count": 24
  }
]
```

---

## 5. Recommended API Execution Order

Run the APIs in this order:

```text
1. POST /admin/generate?seed=42
2. GET /mock/customers?page=1&page_size=5
3. POST /admin/ingest?page_size=10000
4. POST /admin/refresh-analytics
5. GET /analytics/summary
6. GET /analytics/revenue-trends?limit=10
7. GET /analytics/top-customers?limit=10
```

---

## 6. Performance Notes

The analytics APIs are designed to remain below 2 seconds by reading from pre-aggregated tables instead of scanning the full orders and refunds tables on every request.

Load test result:

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
