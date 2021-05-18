import uuid
def make_initials(name):
    a=''
    for thing in name.split():
        a += thing[0].upper()
    return a
class User:
    def __init__(self,name,myhash):
        self.name = name
        self.id = str(uuid.uuid4())
        self.hash = myhash
        self.servers = []
        self.online = False
    @property
    def dict(self):
        return self.__dict__
    def invite(self,server):
        server.members.append(self.id)
        self.servers.append(server)
class Message:
    def __init__(self,content,sender,colour='red'):
        self.content = content
        self.sender = sender.name
        self.colour = colour
class Channel:
    def __init__(self,name):
        self.name = name
        self.id = str(uuid.uuid4())
        self.msgs = []
class Server:
    def __init__(self,name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.members = []
        self.initials = make_initials(name)
        self.channels = []
    def getcbyid(self,myid):
        for c in self.channels:
            if c.id == myid:
                return c