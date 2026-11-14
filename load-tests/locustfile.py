from locust import HttpUser, task, between


class TaskManagerUser(HttpUser):
    wait_time = between(0.5, 1.5)   # each simulated user pauses 0.5-1.5 s between requests

    @task(5)
    def home(self):
        self.client.get("/")

    @task(3)
    def view_tasks(self):
        self.client.get("/tasks")

    @task(1)
    def health(self):
        self.client.get("/health")
