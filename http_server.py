from aiohttp import web
import firebase_admin
from firebase_admin import credentials, firestore
import os

# initialize Firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# routes
async def signup(request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not all([email, password, name]):
        return web.json_response({"error": "Missing fields"}, status=400)

    doc = db.collection("users").document()
    doc.set({
        "email": email,
        "password": password,
        "name": name
    })
    return web.json_response({"message": "User created", "id": doc.id})

async def login(request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    users = db.collection("users").whpassere("email", "==", email).stream()
    for u in users:
        user = u.to_dict()
        if user["password"] == password:
            return web.json_response({"message": "Login successful"})
    return web.json_response({"error": "Invalid credentials"}, status=401)

# start the server
app = web.Application()
app.router.add_post("/signup", signup)
app.router.add_post("/login", login)

web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
