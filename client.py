##A client class type
class Client:
    clientNumber = 0
    def __init__(self, ws):
        Client.clientNumber+=1
        self.username = f"user{Client.clientNumber}"
        self.password = f"password{Client.clientNumber}"
        self.ws = ws
        self.friends = set()
##ENDCLASS
