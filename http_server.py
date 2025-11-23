from aiohttp import web
import aiohttp_cors
import firebase_admin
from firebase_admin import credentials, firestore
import time
import os

# ------------------------------
# FIREBASE INITIALIZATION
# ------------------------------

if os.path.exists("serviceAccountKey.json"):
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
else:
    firebase_admin.initialize_app()

db = firestore.client()


# ------------------------------
# AUTH ROUTES
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

    if not all([email, password]):
        return web.json_response({"error": "Missing fields"}, status=400)

    users = db.collection("users").where("email", "==", email).stream()
    for u in users:
        user = u.to_dict()
        if user.get("password") == password:
            return web.json_response({"message": "Login successful"})

    return web.json_response({"error": "Invalid credentials"}, status=401)


# ------------------------------
# USER ROUTES
# ------------------------------

async def get_users(request):
    users_ref = db.collection("users").stream()
    result = []

    for doc in users_ref:
        d = doc.to_dict()
        result.append({
            "id": doc.id,
            "email": d.get("email"),
            "name": d.get("name")
        })

    return web.json_response(result)


# ------------------------------
# ROOM ROUTES
# ------------------------------

async def create_room(request):
    data = await request.json()
    roomName = data.get("roomName")
    createdBy = data.get("createdBy")

    if not all([roomName, createdBy]):
        return web.json_response({"error": "Missing fields"}, status=400)

    doc = db.collection("rooms").document()
    doc.set({
        "roomName": roomName,
        "createdBy": createdBy
    })

    return web.json_response({"message": "Room created", "roomId": doc.id})


async def get_rooms(request):
    rooms_ref = db.collection("rooms").stream()
    result = []

    for doc in rooms_ref:
        d = doc.to_dict()
        result.append({
            "roomId": doc.id,
            "roomName": d.get("roomName")
        })

    return web.json_response(result)


async def get_room(request):
    roomId = request.match_info["roomId"]
    doc = db.collection("rooms").document(roomId).get()

    if not doc.exists:
        return web.json_response({"error": "Room not found"}, status=404)

    d = doc.to_dict()
    return web.json_response({
        "roomId": roomId,
        "roomName": d.get("roomName"),
        "createdBy": d.get("createdBy")
    })


async def update_room(request):
    roomId = request.match_info["roomId"]
    data = await request.json()
    roomName = data.get("roomName")

    doc_ref = db.collection("rooms").document(roomId)
    doc = doc_ref.get()

    if not doc.exists:
        return web.json_response({"error": "Room not found"}, status=404)

    doc_ref.update({"roomName": roomName})
    return web.json_response({"message": "Room updated"})


async def delete_room(request):
    roomId = request.match_info["roomId"]
    doc = db.collection("rooms").document(roomId).get()

    if not doc.exists:
        return web.json_response({"error": "Room not found"}, status=404)

    db.collection("rooms").document(roomId).delete()
    return web.json_response({"message": "Room deleted"})


# ------------------------------
# CONVERSATION ROUTES
# ------------------------------

async def create_conversation(request):
    data = await request.json()
    userA = data.get("userA")
    userB = data.get("userB")

    if not all([userA, userB]):
        return web.json_response({"error": "Missing fields"}, status=400)

    doc = db.collection("conversations").document()
    doc.set({
        "userA": userA,
        "userB": userB
    })

    return web.json_response({"message": "Conversation created", "conversationId": doc.id})


async def get_conversation(request):
    conversationId = request.match_info["conversationId"]
    doc = db.collection("conversations").document(conversationId).get()

    if not doc.exists:
        return web.json_response({"error": "Conversation not found"}, status=404)

    d = doc.to_dict()
    return web.json_response({
        "conversationId": conversationId,
        "participants": [d.get("userA"), d.get("userB")]
    })


# ------------------------------
# MESSAGE ROUTES
# ------------------------------

async def send_message(request):
    data = await request.json()
    senderId = data.get("senderId")
    roomId = data.get("roomId")
    conversationId = data.get("conversationId")
    message_text = data.get("message")

    if not senderId or not message_text:
        return web.json_response({"error": "Missing fields"}, status=400)

    if not roomId and not conversationId:
        return web.json_response({"error": "Missing fields"}, status=400)

    # Check existence
    if roomId:
        if not db.collection("rooms").document(roomId).get().exists:
            return web.json_response({"error": "Room not found"}, status=404)

    if conversationId:
        if not db.collection("conversations").document(conversationId).get().exists:
            return web.json_response({"error": "Conversation not found"}, status=404)

    doc = db.collection("messages").document()
    doc.set({
        "senderId": senderId,
        "roomId": roomId,
        "conversationId": conversationId,
        "message": message_text,
        "timestamp": int(time.time())
    })

    return web.json_response({"message": "Message sent", "messageId": doc.id})


async def get_room_messages(request):
    roomId = request.match_info["roomId"]

    if not db.collection("rooms").document(roomId).get().exists:
        return web.json_response({"error": "Room not found"}, status=404)

    msgs = db.collection("messages").where("roomId", "==", roomId).stream()

    result = []
    for m in msgs:
        d = m.to_dict()
        result.append({
            "messageId": m.id,
            "senderId": d.get("senderId"),
            "message": d.get("message"),
            "timestamp": d.get("timestamp")
        })

    return web.json_response(result)


async def get_conversation_messages(request):
    conversationId = request.match_info["conversationId"]

    if not db.collection("conversations").document(conversationId).get().exists:
        return web.json_response({"error": "Conversation not found"}, status=404)

    msgs = db.collection("messages").where("conversationId", "==", conversationId).stream()

    result = []
    for m in msgs:
        d = m.to_dict()
        result.append({
            "messageId": m.id,
            "senderId": d.get("senderId"),
            "message": d.get("message"),
            "timestamp": d.get("timestamp")
        })

    return web.json_response(result)


# ------------------------------
# ROOT
# ------------------------------

async def root(request):
    return web.json_response({"message": "Server is running"})


# ------------------------------
# APP SETUP
# ------------------------------

app = web.Application()

# Auth
app.router.add_post("/signup", signup)
app.router.add_post("/login", login)

# Users
app.router.add_get("/users", get_users)

# Rooms
app.router.add_post("/rooms", create_room)
app.router.add_get("/rooms", get_rooms)
app.router.add_get("/rooms/{roomId}", get_room)
app.router.add_post("/rooms/{roomId}", update_room)
app.router.add_post("/rooms/{roomId}/delete", delete_room)

# Conversations
app.router.add_post("/conversations", create_conversation)
app.router.add_get("/conversations/{conversationId}", get_conversation)

# Messages
app.router.add_post("/messages", send_message)
app.router.add_get("/rooms/{roomId}/messages", get_room_messages)
app.router.add_get("/conversations/{conversationId}/messages", get_conversation_messages)

# Root
app.router.add_get("/", root)

# CORS
cors = aiohttp_cors.setup(app, defaults={
    "http://localhost:3000": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
        allow_methods=["GET", "POST", "OPTIONS"]
    )
})

for route in list(app.router.routes()):
    cors.add(route)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
