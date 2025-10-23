##A client class type
##Clients have: an ID, a username, a password, and a set of friendlist (saved as their usernames)
class Client:
    ##TODO: keep client number persistent

    ##default init
    def __init__(self, username, password, ID, friendlist=set()):
        self.username = username
        self.password = password
        self.friendlist = friendlist #Saved as a set of user IDs
        self.ID = ID
        self.online = True

    ##returns new client in a dict for writing to the db
    def getData(self):
        return {
            "username":self.username,
            "password":self.password,
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
