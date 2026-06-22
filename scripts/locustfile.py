from locust import HttpUser, task, between


class AnalyticsUser(HttpUser):
    wait_time = between(0.1, 1.0)

    @task(5)
    def summary(self):
        self.client.get("/analytics/summary")

    @task(3)
    def revenue_trends(self):
        self.client.get("/analytics/revenue-trends?limit=30")

    @task(3)
    def top_customers(self):
        self.client.get("/analytics/top-customers?limit=10")

    @task(1)
    def health(self):
        self.client.get("/health")