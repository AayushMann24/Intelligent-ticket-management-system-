from agents.api_client import APIClient

api = APIClient()

print("Logging in...")

token = api.login(
    "ayush.mann124@gmail.com",
    "ITMS@1234"
)

print("Login Successful")
print(token)

print("\nFetching tickets...\n")

tickets = api.get("/tickets")

print(tickets)