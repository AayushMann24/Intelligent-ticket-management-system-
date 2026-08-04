import requests

BASE_URL = "http://localhost:8000"

class APIClient:

    def __init__(self):
        self.base_url = BASE_URL
        self.token = None

    def login(self, email: str, password: str):

        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": email,
                "password": password
            }
        )

        if response.status_code != 200:
            raise Exception(
                f"Login failed: {response.text}"
            )

        self.token = response.json()["access_token"]

        return self.token

    def headers(self):

        if not self.token:
            raise Exception("Please login first.")

        return {
            "Authorization": f"Bearer {self.token}"
        }

    def get(self, endpoint):

        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers()
        )

        return response.json()

    def post(self, endpoint, data):

        response = requests.post(
            f"{self.base_url}{endpoint}",
            json=data,
            headers=self.headers()
        )

        return response.json()

    def put(self, endpoint, data):

        response = requests.put(
            f"{self.base_url}{endpoint}",
            json=data,
            headers=self.headers()
        )

        return response.json()

    def delete(self, endpoint):

        response = requests.delete(
            f"{self.base_url}{endpoint}",
            headers=self.headers()
        )

        return response.json()