from firebase_admin import credentials, firestore, initialize_app
from client import *
import hashlib
##TODO: Break apis up into the following scheme
#/
#-routes
#--client_api.py
#--admin_api.py
#--etc

##init connection
cred = credentials.Certificate("../chatbase-b273c-firebase-adminsdk-fbsvc-4287cc06fa.json")
initialize_app(cred)
db = firestore.client()
clientDict = db.collection("misc").document("client").get().to_dict()
if clientDict == None:
    numberOfClients = 0
else:
    numberOfClients = clientDict["clientNum"]


##Return new client object for signing in
def userSignIn(username, password):
    user_refs=db.collection("users").list_documents()
    for user in user_refs:
        user = user.get().to_dict()
        if user["username"] == username:
            #get the salt and hash the password
            password = user["password"]
            salt = user["salt"]
            pw_hashed = hashlib.sha256((password + salt).encode())
            if user["password"] == password:
                return Client(user, password, salt, user["ID"], user["friendlist"])
            else:
                print(f"ERR: PASSWORD IS INCORRECT")
                return None
    else:
        print(f"ERR: {username} WAS NOT FOUND")
        return None
    ##ENDFOR

##END userSignIn

##add new user to db
def addUserToDB(client):
    global numberOfClients
    data = client.getData()
    username=data["username"]
    if db.collection("users").document(username).get().to_dict():
        print(f"ERR: {username} ALREADY EXISTS")
        return
    ##ENDIF
    db.collection("users").document(username).set(data)
    numberOfClients+=1
    db.collection("misc").document("client").set({"clientNum":numberOfClients})
##END addUserToDB

##Delete a user from the db
def deleteUser(username):
    global numberOfClients
    user=db.collection("users").document(username)
    if not user.get().to_dict():
        print(f"ERR: {username} WAS NOT FOUND")
        return None
    ##ENDIF
    user.delete()
    print(f"User {username} was removed from the database")
    numberOfClients-=1
    db.collection("misc").document("client").set({"clientNum":numberOfClients})
##END deleteUser

##TODO: implement requesting
##Adds a friend to a client's friendlist
def addFriend(client, friend):
    client.addFriend(friend)
    friend.addFriend(client)
    db.collection("user").document(client.username).update({"friendlist":client.friendlist})
    db.collection("user").document(friend.username).update({"friendlist":friend.friendlist})
##END addFriend

##Tool for creating test user
def _addTestUser():
    client = Client("John Smith", "password", numberOfClients)
    addUserToDB(client)
    print("John smith was added successfully")
##END _addTestUser

def _addTestUser2():
    client = Client("Jane Doe", "password1", numberOfClients)
    addUserToDB(client)
    print("Jane Doe was added successfully")
##END _addTestUser2

##Check if a user exists
def checkUser(username):
    for client_ref in db.collection("users").list_documents():
        client = client_ref.get()
        if client["username"] == username:
            print(f"{username} found")
            return True
        ##ENDIF
    else:
        print(f"ERR: {username} WAS NOT FOUND")
        return False
    ##ENDFOR

if __name__ == "__main__":
    pass
    # client = Client("John Smith", "password", numberOfClients)
    # print(client.password_hex)
    # print(f"Client count = {numberOfClients}")
    # _addTestUser()
    # print(f"Client count = {numberOfClients}")
    # deleteUser("John Smith")
    # _addTestUser2()
    # print(f"Client count = {numberOfClients}")
    # _addTestUser()
    # print(f"Client count = {numberOfClients}")
    # deleteUser("Jane Doe")
    # deleteUser("John Smith")
    # print(f"Client count = {numberOfClients}")
    # print(numberOfClients)
##ENDIF
