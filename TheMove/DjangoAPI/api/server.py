import socket 
import threading
import collections
from weakref import ref
import string
import random

###########################################################################
#Global variables

#all votes
votes = [0] * 10

#dictionary of user/vote pairs
dictionary = {"placeholder":-1}

IDLENGTH = 5
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
REFRESH_MESSAGE = "!REFRESH"
VERIFY_ID_MESSAGE = "!VERIFY_ID"
NEW_ID_MESSAGE = "!NEW_ID_REQUEST"
VERIFIED_MESSAGE = "!VERIFIED"
NOT_VERIFIED_MESSAGE = "!NOT_VERIFIED"
PLACEHOLDER = "tmp"
###########################################################################

###########################################################################
#bind server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #make a new server

# Avoid bind() exception: OSError: [Errno 48] Address already in use
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)
###########################################################################

###########################################################################
#reset votes and IDs every day
def resetServer():
    pass
###########################################################################


###########################################################################
#user identification methods
#users can get a new daily ID
#old users must enter their ID to vote and get server data
#users can request a new ID if they forgot theirs
#all IDs are reset/removed at the end of each day

#ID is stored only in server, once ID is checked, client is updated to store
#the ID, and the ID is sent along with the vote whenever the client votes

def generateUserID():
    #characters = string.ascii_lowercase + string.digits
    characters = string.digits
    ID = ''.join(random.choice(characters) for i in range(IDLENGTH))

    #if ID is already used
    while (ID in dictionary):
        ID = ''.join(random.choice(characters) for i in range(IDLENGTH))

    dictionary[ID] = -1 #add user to dictionary
    return ID

def sendNewID(conn):
    ID = generateUserID()
    conn.send(ID.encode(FORMAT))

def verifyUserID(conn, ID):
    if ID in dictionary:
        conn.send(VERIFIED_MESSAGE.encode(FORMAT))
        return True
    else: 
        conn.send(NOT_VERIFIED_MESSAGE.encode(FORMAT))
        return False
###########################################################################



###########################################################################
#update votes on client and server

def refreshClient(conn, clientID):
    votesAsString = convertListToString(clientID) #votesAsString includes user's vote at the end
    conn.send(votesAsString.encode(FORMAT)) 
    #conn.send(str(dictionary[clientID]).encode(FORMAT))


def updateServer(id, msg):
    newVote = int(msg)
    if (id in dictionary):
        if dictionary[id] == -1: #if connected user hasn't voted, increment new vote
            votes[newVote] += 1
        else: 
            votes[dictionary[id]] -= 1 #if they've voted, decrement old vote, increment new vote
            votes[newVote] += 1

    dictionary[id] = newVote #update dictionary of user and latest vote
    print(votes)

#convert server vote data to a list
def convertListToString(clientID):
    votesAsString = ""
    for x in votes:
        votesAsString += " " + str(x)
    votesAsString += " " + str(dictionary[clientID])
    return votesAsString
###########################################################################


###########################################################################
#server client connection
#this function handles all requests from client
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected: 
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            id, msg = msg.split()
            if msg == DISCONNECT_MESSAGE:
                connected = False
                break
            if msg == REFRESH_MESSAGE:  #client wants to refresh votes
                refreshClient(conn, id)
            elif msg == NEW_ID_MESSAGE: #client wants new ID
                sendNewID(conn)
            elif msg == VERIFY_ID_MESSAGE: #client is logging in
                isVerified = verifyUserID(conn, id)
                if isVerified:
                    #pass
                    refreshClient(conn, id) #refresh only if client is verified
            else: #client voted
                updateServer(id, msg)
                refreshClient(conn, id)

            #print(f"[{addr}] {msg}")
    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True: 
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}") #start thread always running so minus 1

print("[STARTING] server is starting...")
start()
###########################################################################