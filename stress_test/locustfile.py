from locust import HttpUser, between, task

VISIT_URL = "https://visit-counter-dot-taller3-proca.ue.r.appspot.com"

class WebsiteUser(HttpUser):
    wait_time = between(5, 30)

    @task(50)
    def home(self):
        self.client.get("")
        self.client.get("static/home1.jpeg")
        self.client.get("static/home2.jpeg")
        self.client.get("static/home3.jpeg")
        self.client.get("static/home4.jpeg")
        self.client.get(VISIT_URL + "/visits?key=institutional_home")

    @task(10)
    def about(self):
        self.client.get("about")
        self.client.get("static/mon-2015083_chartx50667a01.jpg")
        self.client.get(VISIT_URL + "/visits?key=institutional_about")

    @task(2)
    def jobs(self):
        self.client.get("jobs")
        self.client.get(VISIT_URL + "/visits?key=institutional_jobs")

    @task(1)
    def legal(self):
        self.client.get("legal")
        self.client.get(VISIT_URL + "/visits?key=institutional_legal")