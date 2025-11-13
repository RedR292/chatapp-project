import http.client
import json

# Connect to the running server
conn = http.client.HTTPConnection("localhost", 8080)

# User credentials (must match what you used in signup)
payload = json.dumps({
    "email": "test@example.com",
    "password": "123456"
})
headers = {"Content-Type": "application/json"}

# Send POST request to /login
conn.request("POST", "/login", payload, headers)
res = conn.getresponse()

# Print response status and content
print(res.status, res.reason)
print(res.read().decode())
