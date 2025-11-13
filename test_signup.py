import http.client
import json

conn = http.client.HTTPConnection("localhost", 8080)
payload = json.dumps({
    "email": "test@example.com",
    "password": "123456",
    "name": "Test User"
})
headers = {"Content-Type": "application/json"}

conn.request("POST", "/signup", payload, headers)
res = conn.getresponse()
print(res.status, res.reason)
print(res.read().decode())
