from locust import HttpUser, task


class FactorialTest(HttpUser):

    @task
    def endpoint1(self):
        self.client.get(f"/prime/5")

    @task
    def endpoint2(self):
        self.client.get(f"/prime/12")