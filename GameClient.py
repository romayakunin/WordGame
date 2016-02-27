import sys
import socket

host = socket.gethostname()
if len(sys.argv) == 2:
    host = sys.argv[1]
address = (host, 12345)
print "Server address:", address

try:
    sender = socket.socket()
    try:
        sender.connect(address)
        print "Connected to server."
        while True:
            message = raw_input("> ")
            if message == "/exit":
                break
            sender.send(message)
            reply = sender.recv(10000)
            print "<", reply
    finally:
        sender.close()
except Exception as e:
    print "Error:", e
