from locust import HttpUser, task
import random


class FactorialTest(HttpUser):

    @task
    def endpoint1(self):
        self.client.get(f"/prime/5")