from firebase_admin import credentials, firestore, initialize_app

##init connection
cred = credentials.Certificate("chatbase-b273c-firebase-adminsdk-fbsvc-4287cc06fa.json")
initialize_app(cred)
db = firestore.client()

##Read from db
user_ref = db.collection("users").document("user1")
user = user_ref.get()
print(user.to_dict())

##Write to db
c = Client(
