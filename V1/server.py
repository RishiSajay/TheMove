import socket 
import threading

votes = [0] * 10
HEADER = 64
PORT = 5050
#SERVER = "192.168.1.147" command line -> ipconfig -> ipv4
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #make a new server
server.bind(ADDR)
#server specific methods
def updateServer(msg):
    oldVote, newVote = msg.split()
    oldVote = int(oldVote)
    newVote = int(newVote)
    if (oldVote != -1):
        votes[oldVote] -= 1
    votes[newVote] += 1
    print(votes)

def convertListToString():
    votesAsString = ""
    for x in votes:
        votesAsString += " " + str(x)
    return votesAsString

#server client connection
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected: 
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            updateServer(msg)
            #print(f"[{addr}] {msg}")
            votesAsString = convertListToString()
            conn.send(votesAsString.encode(FORMAT))
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