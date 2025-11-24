from aiohttp import web
import aiohttp_cors
import firebase_admin
from firebase_admin import credentials, firestore
import time
import os
import hashlib
import base64
import secrets
import uuid
import datetime
from google.cloud import storage
from google.oauth2 import service_account

# ------------------------------
# HELPER METHODS
# ------------------------------

# HASHING HELPERS
def _hash(pw: str):
    salt = secrets.token_urlsafe(32)
    pw_salted = pw + salt
    pw_hashed = hashlib.sha256(pw_salted.encode()).hexdigest()
    return pw_hashed, salt

def _get_hash(pw: str, salt: str):
    if salt is None:
        raise ValueError("Salt is missing for this user")
    pw_salted = pw + salt
    pw_hashed = hashlib.sha256(pw_salted.encode()).hexdigest()
    return pw_hashed

# ------------------------------
# FIRESTORE DATABASE INITIALIZATION
# ------------------------------

if os.path.exists("serviceAccountKey.json"):
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
else:
    firebase_admin.initialize_app()

db = firestore.client()

# ------------------------------
# FIREBASE STORAGE INITIALIZATION
# ------------------------------

if os.path.exists("serviceAccountKey.json"):
    storage_credentials = service_account.Credentials.from_service_account_file(
        "serviceAccountKey.json"
    )
    storage_client = storage.Client(credentials=storage_credentials)
else:
    storage_client = storage.Client()

bucket = storage_client.bucket("chatbase-b273c.firebasestorage.app")

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

    password_hash, salt = _hash(password)

    doc = db.collection("users").document()
    doc.set({
        "email": email,
        "password": password_hash,
        "hash_salt": salt,
        "name": name,
        "friends": [],
        "incomingRequests": []
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
        salt = user.get("hash_salt")
        if salt is None:
            continue
        password_hashed = _get_hash(password, salt)
        if user.get("password") == password_hashed:
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
# FRIEND SYSTEM ROUTES
# ------------------------------

async def send_friend_request(request):
    data = await request.json()
    fromUser = data.get("fromUser")
    toUser = data.get("toUser")

    if not all([fromUser, toUser]):
        return web.json_response({"error": "Missing fields"}, status=400)

    if fromUser == toUser:
        return web.json_response({"error": "Cannot friend yourself"}, status=400)

    from_ref = db.collection("users").document(fromUser).get()
    to_ref = db.collection("users").document(toUser).get()

    if not from_ref.exists or not to_ref.exists:
        return web.json_response({"error": "User not found"}, status=404)

    to_data = to_ref.to_dict()

    if fromUser in to_data.get("friends", []):
        return web.json_response({"error": "Already friends"}, status=400)

    if fromUser in to_data.get("incomingRequests", []):
        return web.json_response({"error": "Request already sent"}, status=400)

    db.collection("users").document(toUser).update({
        "incomingRequests": firestore.ArrayUnion([fromUser])
    })

    return web.json_response({"message": "Friend request sent"})

async def accept_friend_request(request):
    data = await request.json()
    userId = data.get("userId")
    fromUser = data.get("fromUser")

    if not all([userId, fromUser]):
        return web.json_response({"error": "Missing fields"}, status=400)

    user_doc = db.collection("users").document(userId).get()
    from_doc = db.collection("users").document(fromUser).get()

    if not user_doc.exists or not from_doc.exists:
        return web.json_response({"error": "User not found"}, status=404)

    user_data = user_doc.to_dict()

    if fromUser not in user_data.get("incomingRequests", []):
        return web.json_response({"error": "No friend request found"}, status=400)

    db.collection("users").document(userId).update({
        "incomingRequests": firestore.ArrayRemove([fromUser]),
        "friends": firestore.ArrayUnion([fromUser])
    })

    db.collection("users").document(fromUser).update({
        "friends": firestore.ArrayUnion([userId])
    })

    return web.json_response({"message": "Friend request accepted"})

async def get_friends(request):
    userId = request.match_info["userId"]
    doc = db.collection("users").document(userId).get()

    if not doc.exists:
        return web.json_response({"error": "User not found"}, status=404)

    data = doc.to_dict()
    return web.json_response({"friends": data.get("friends", [])})

async def get_incoming_requests(request):
    userId = request.match_info["userId"]
    doc = db.collection("users").document(userId).get()

    if not doc.exists:
        return web.json_response({"error": "User not found"}, status=404)

    data = doc.to_dict()
    return web.json_response({"incomingRequests": data.get("incomingRequests", [])})

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
# MESSAGE ROUTES (USING PUBLIC URLS)
# ------------------------------

async def send_message(request):
    data = await request.json()
    senderId = data.get("senderId")
    roomId = data.get("roomId")
    conversationId = data.get("conversationId")
    message_text = data.get("message")
    message_document = data.get("document")  # {filename, data}

    if not senderId or not message_text:
        return web.json_response({"error": "Missing fields"}, status=400)

    if not roomId and not conversationId:
        return web.json_response({"error": "Missing fields"}, status=400)

    # Validate room or conversation
    if roomId and not db.collection("rooms").document(roomId).get().exists:
        return web.json_response({"error": "Room not found"}, status=404)

    if conversationId and not db.collection("conversations").document(conversationId).get().exists:
        return web.json_response({"error": "Conversation not found"}, status=404)

    document_url = None

    if message_document:
        filename = message_document.get("filename")
        data_b64 = message_document.get("data")

        if not filename.endswith(".pdf"):
            return web.json_response({"error": "Document is not a pdf"}, status=400)

        file_bytes = base64.b64decode(data_b64)
        blob_name = f"messages/{uuid.uuid4()}-{filename}"
        blob = bucket.blob(blob_name)

        blob.upload_from_string(
            file_bytes,
            content_type="application/pdf"
        )

        document_url = blob.public_url

    doc = db.collection("messages").document()
    doc.set({
        "senderId": senderId,
        "roomId": roomId,
        "conversationId": conversationId,
        "message": message_text,
        "document": document_url,
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
            "document": d.get("document"),  # public URL
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
            "document": d.get("document"),  # public URL
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

app = web.Application(client_max_size=10*1024*1024)

# Auth
app.router.add_post("/signup", signup)
app.router.add_post("/login", login)

# Users
app.router.add_get("/users", get_users)

# Friends
app.router.add_post("/friends/request", send_friend_request)
app.router.add_post("/friends/accept", accept_friend_request)
app.router.add_get("/friends/{userId}", get_friends)
app.router.add_get("/friends/{userId}/incoming", get_incoming_requests)

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
