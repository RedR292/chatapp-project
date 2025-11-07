import secrets
import hashlib
##A client class type
##Clients have: an ID, a username, a password, and a set of friendlist (saved as their usernames)

##Encrypt passwords using SHA256 algorithim
def _hash(pw):
    salt = secrets.token_urlsafe(32) #generates 32B salt
    pw_salted = pw + salt
    pw_hashed = hashlib.sha256(pw_salted.encode())
    return (pw_hashed.hexdigest(), salt)
##END _hash

class Client:
    ##TODO: Implement password encryption

    ##default init
    def __init__(self, username, password, ID, friendlist=set()):
        self.username = username
        self.password_hex, self.salt = _hash(password)
        self.friendlist = friendlist #Saved as a set of user IDs
        self.ID = ID
        self.online = True

    ##returns new client in a dict for writing to the db
    def getData(self):
        return {
            "username":self.username,
            "password":self.password_hex,
            "salt":self.salt,
            "ID":self.ID,
            "friendlist":self.friendlist,
            "online":True
        }
    ##END getData

    def __str__(self):
        return f"Name: {self.username}\
        \nPassword: {self.password}\
        \nFriends: {self.friendlist}"
    ##ENDSTR

    ##Add a friend
    def addFriend(self, friend):
        self.friendlist.add(friend.ID)
    ##END addFriend

    ##Remove a friend
    def removeFriend(self, ID):
        self.friendlist.remove(ID)
    ##END removeFriend
##ENDCLASS
