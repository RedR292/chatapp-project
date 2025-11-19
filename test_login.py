import sys
import json
from urllib.parse import urlparse
import http.client

# ------------------------------
# Get base URL
# ------------------------------
if len(sys.argv) > 1:
    base_url = sys.argv[1].rstrip("/")
else:
    base_url = "http://localhost:8080"

parsed_url = urlparse(base_url)
host = parsed_url.hostname
port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
use_https = parsed_url.scheme == "https"

# ------------------------------
# Connect to server
# ------------------------------
conn = http.client.HTTPSConnection(host, port) if use_https else http.client.HTTPConnection(host, port)

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
