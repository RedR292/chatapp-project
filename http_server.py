from aiohttp import web
import firebase_admin
from firebase_admin import credentials, firestore
import os
<<<<<<< HEAD
=======

# ------------------------------
# FIREBASE INITIALIZATION
# ------------------------------

# Use service account JSON locally if it exists, otherwise default credentials
if os.path.exists("serviceAccountKey.json"):
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
else:
    # Cloud Run / GCP: uses built-in credentials automatically
    firebase_admin.initialize_app()
>>>>>>> 55926c8833fad0283c02634832d25fadae176159

db = firestore.client()

# ------------------------------
# ROUTES
# ------------------------------

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

<<<<<<< HEAD
    users = db.collection("users").whpassere("email", "==", email).stream()
=======
    if not all([email, password]):
        return web.json_response({"error": "Missing fields"}, status=400)

    users = db.collection("users").where("email", "==", email).stream()
>>>>>>> 55926c8833fad0283c02634832d25fadae176159
    for u in users:
        user = u.to_dict()
        if user.get("password") == password:
            return web.json_response({"message": "Login successful"})

    return web.json_response({"error": "Invalid credentials"}, status=401)


# ------------------------------
# GET REQUEST TO THE ROOT ENDPOINT TO SHOW THAT THE SERVER IS RUNNING
# ------------------------------

async def root(request):
    return web.json_response({"message": "Server is running"})


# ------------------------------
# APP SETUP
# ------------------------------

app = web.Application()
app.router.add_post("/signup", signup)
app.router.add_post("/login", login)
app.router.add_get("/", root)  # <-- Added root route

<<<<<<< HEAD
web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
=======
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
>>>>>>> 55926c8833fad0283c02634832d25fadae176159
