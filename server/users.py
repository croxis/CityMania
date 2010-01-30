'''User management system and database. Stores users, their passwords, 
check access levels, and so on.

userdb = {"username": {"password": password, "access": LEVEL, "loggedin": BOOL, "peer": (peer,peer)}
Access levels:
OBSERVER: Can only observe region and cities with permission for that user to observe. Good for guests
NORMAL: Normal player with no server level privlidges
GM: Game master, can ban, unban, kick, delete any city, save (but not load), delete users. Can move users to and from observer mode. A moderator to use forum speak. 
ADMIN: Full server control. Load and new Games. Can stop or start the server. Can promote anyone to GM, observer, normal or admin.
OWNER: Top level. Can only promote others to owner, but this is a non reversible process. Can not be demoted.

The permission system is progressive, so permission checking will check to see if the user is that level or greater.

loggedin and peer are to check that the user is logged in and the peer to contact them by.

It *may* be needed that the user will need to be a class other than the dict, so we will still abstract what we need through functions
'''

# Access levels
OBSERVER = 0
NORMAL = 1
GM = 2
ADMIN = 3
OWNER = 4

ACCESS = {"observer": OBSERVER, "normal": NORMAL, "gm": GM, "admin": ADMIN, "owner": OWNER}

userdb = {}

# TODO: Dehardcode access level
def addUser(name, password, access="normal"):
    '''Add user to database. access variable is lowercase string.
    If there is no user in the database then the first one added will be the owner'''
    if userdb:
        userdb[name] = {"password": password, "access": ACCESS[access], "loggedin": False, "peer": None}
    else:
        userdb[name] = {"password": password, "access": OWNER, "loggedin": False, "peer": None}

def login(name, password, peer):
    '''Adds new user to db. Does not auto logon. Returns 0 if not in db, 1 if password does not match, 2 if success'''
    if password == userdb[name]["password"]:
        userdb[name]["loggedin"] = True
        if userdb[name]["peer"]:
            # This user is already logged in, so we need to log out the old ip
            # container = error message telling old connection new one has been made
            #messenger.send("sendData", [peer, container])
            print "Kicking out", name, peer
            messenger.send("logout", [userdb[name]["peer"]])
        userdb[name]["peer"] = peer
        return 1
    return 0

def logout(name):
    userdb[name]["loggedin"] = False
    userdb[name]["peer"] = None
    print "In users module, logged out", name, userdb

def getType(name):
    '''Returns the user type'''
    return userdb[name]["access"]

def getNameFromPeer(peer):
    '''Messy function to get a user name from the peer.'''
    for name, values in userdb.items():
        if values["peer"] is peer:
            return name

# Check permission for whatever
def isOwner(name):
    if userdb[name]["access"] is OWNER:
        return True

def isAdmin(name):
    if userdb[name]["access"] >= ADMIN:
        return True

def isGm(name):
    if userdb[name]["access"] >= GM:
        return True

def isNormal(name):
    if userdb[name]["access"] >= NORMAL:
        return True

def isObserver(name):
    if userdb[name]["access"] >= OBSERVER:
        return True
    
