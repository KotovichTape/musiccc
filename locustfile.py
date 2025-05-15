from locust import HttpUser, task, between
from random import choice

class MusicRentalUser(HttpUser):
    wait_time = between(1, 3)  
    

    @task(3)
    def view_equipment_catalog(self):
        self.client.get("/")
        self.client.get("/equipment/")
