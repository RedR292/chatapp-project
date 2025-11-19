import requests
import sys

# ------------------------------
# Get the base URL
# ------------------------------
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1].rstrip("/")  # Use provided URL
else:
    BASE_URL = "http://localhost:8080"   # Default to localhost

# ------------------------------
# Test Signup
# ------------------------------
signup_url = f"{BASE_URL}/signup"
data = {
    "email": "test@example.com",
    "password": "123",
    "name": "Test User"
}

response = requests.post(signup_url, json=data)
print("Signup response:", response.json())
