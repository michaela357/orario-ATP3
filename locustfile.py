from locust import HttpUser, task, between
import random

class OrarioUser(HttpUser):

    wait_time = between(2, 5)
    
    def on_start(self):
        # Store created task IDs for this user
        self.task_ids = []
        response = self.client.post(
            "/login",
            data={
                "email": "test@email.com",
                "password": "banana1!Q"
            },
            allow_redirects=True
        )

        if response.status_code != 200:
            print("Login failed:", response.status_code)

    @task(6)
    def add_task(self):
        response = self.client.post(
            "/api/add_task",
            data={
                "title": f"Load Test Task {random.randint(1, 999999)}",
                "description": "Created during Locust performance testing",
                "due_date": "2026-12-31"
            })

        if response.status_code == 200:
            try:
                task_id = response.json()["task_id"]
                self.task_ids.append(task_id)
            except:
                pass

    @task(5)
    def edit_task(self):
        if self.task_ids:
            task_id = random.choice(self.task_ids)
            self.client.post(
                f"/api/edit_task/{task_id}",
                data={
                    "title": "Updated Load Test Task",
                    "description": "Edited by Locust",
                    "due_date": "2026-12-31"
                })

    @task(4)
    def complete_task(self):
        if self.task_ids:
            task_id = random.choice(self.task_ids)
            self.client.post(f"/api/complete_task/{task_id}")

    @task(4)
    def dashboard(self):
        self.client.get("/dashboard")

    @task(3)
    def view_tasks(self):
        self.client.get("/api/get_tasks")

    @task(3)
    def pomodoro_dashboard(self):
        self.client.get("/timer_dashboard")

    @task(2)
    def flashcards_page(self):
        self.client.get("/flashcards")

    @task(1)
    def save_study_time(self):
        self.client.post("/api/save_study_time",
            json={
                "minutes": 1
            })