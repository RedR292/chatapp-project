import requests
import json
import time
import base64  # added for PDF encoding

BASE = "https://chatapp-1027679917959.us-central1.run.app"

def pretty(label, res):
    print(f"\n==== {label} ====")
    print("Status:", res.status_code)
    try:
        print("Response:", json.dumps(res.json(), indent=2))
    except:
        print("Non-JSON Response:", res.text)


# -------------------------
# SIGNUP TESTS
# -------------------------
r1 = requests.post(f"{BASE}/signup", json={
    "email": "alice@example.com",
    "password": "123",
    "name": "Alice"
})
pretty("Signup Alice", r1)
alice_id = r1.json().get("id")

r2 = requests.post(f"{BASE}/signup", json={
    "email": "bob@example.com",
    "password": "456",
    "name": "Bob"
})
pretty("Signup Bob", r2)
bob_id = r2.json().get("id")


# -------------------------
# LOGIN TESTS
# -------------------------
pretty("Login Alice", requests.post(f"{BASE}/login", json={
    "email": "alice@example.com",
    "password": "123"
}))

pretty("Login Bob", requests.post(f"{BASE}/login", json={
    "email": "bob@example.com",
    "password": "456"
}))


# -------------------------
# GET USERS
# -------------------------
pretty("Get Users", requests.get(f"{BASE}/users"))


# -------------------------
# FRIEND SYSTEM TESTS
# -------------------------

# SEND FRIEND REQUEST
pretty("Alice sends friend request to Bob", 
       requests.post(f"{BASE}/friends/request", json={
           "fromUser": alice_id,
           "toUser": bob_id
       }))

# GET INCOMING REQUESTS FOR BOB
pretty("Bob views incoming friend requests", 
       requests.get(f"{BASE}/friends/{bob_id}/incoming"))

# ACCEPT REQUEST (Bob accepts Alice)
pretty("Bob accepts Alice's friend request",
       requests.post(f"{BASE}/friends/accept", json={
           "userId": bob_id,
           "fromUser": alice_id
       }))

# GET FINAL FRIEND LISTS
pretty("Alice's friends", requests.get(f"{BASE}/friends/{alice_id}"))
pretty("Bob's friends", requests.get(f"{BASE}/friends/{bob_id}"))


# -------------------------
# CREATE ROOMS
# -------------------------
r3 = requests.post(f"{BASE}/rooms", json={
    "roomName": "General",
    "createdBy": alice_id
})
pretty("Create Room (General)", r3)
room1 = r3.json().get("roomId")


r4 = requests.post(f"{BASE}/rooms", json={
    "roomName": "Gaming",
    "createdBy": bob_id
})
pretty("Create Room (Gaming)", r4)
room2 = r4.json().get("roomId")


# -------------------------
# GET ROOMS
# -------------------------
pretty("Get All Rooms", requests.get(f"{BASE}/rooms"))


# -------------------------
# GET SPECIFIC ROOM
# -------------------------
pretty("Get Room 1", requests.get(f"{BASE}/rooms/{room1}"))


# -------------------------
# UPDATE ROOM
# -------------------------
pretty("Update Room 1", requests.post(f"{BASE}/rooms/{room1}", json={
    "roomName": "General Chat"
}))


# -------------------------
# CREATE CONVERSATION
# -------------------------
r5 = requests.post(f"{BASE}/conversations", json={
    "userA": alice_id,
    "userB": bob_id
})
pretty("Create Conversation Alice <-> Bob", r5)
conv_id = r5.json().get("conversationId")


# -------------------------
# GET CONVERSATION
# -------------------------
pretty("Get Conversation", requests.get(f"{BASE}/conversations/{conv_id}"))


# -------------------------
# SEND MESSAGES
# -------------------------
pretty("Send Message to Room 1", requests.post(f"{BASE}/messages", json={
    "senderId": alice_id,
    "roomId": room1,
    "conversationId": None,
    "message": "Hello from Alice!"
}))

time.sleep(1)

pretty("Send Message to Conversation", requests.post(f"{BASE}/messages", json={
    "senderId": bob_id,
    "roomId": None,
    "conversationId": conv_id,
    "message": "Hey Alice, this is Bob!"
}))

# -------------------------
# SEND MESSAGE WITH DOCUMENT
# -------------------------
# Requires 'test.pdf' file in the same folder
with open("test.pdf", "rb") as f:
    pdf_bytes = f.read()
pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

pretty("Send Message with PDF Document", requests.post(f"{BASE}/messages", json={
    "senderId": alice_id,
    "roomId": room1,
    "conversationId": None,
    "message": "Here is a PDF document",
    "document": {
        "filename": "test.pdf",
        "data": pdf_b64
    }
}))


# -------------------------
# GET ROOM MESSAGES
# -------------------------
pretty("Messages in Room 1", requests.get(f"{BASE}/rooms/{room1}/messages"))


# -------------------------
# GET CONVERSATION MESSAGES
# -------------------------
pretty("Messages in Conversation", requests.get(
    f"{BASE}/conversations/{conv_id}/messages"
))


# -------------------------
# DELETE ROOM
# -------------------------
pretty("Delete Room 1", requests.post(f"{BASE}/rooms/{room1}/delete"))


print("\n==== TESTING COMPLETE ====")
