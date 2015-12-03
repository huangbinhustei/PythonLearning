import socket

svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

svr.bind(("127.0.0.1", 9999))

svr.listen(1)
print("w 8 4 connection...")
sock, cli = svr.accept()

while True:
    data = client.recv(1024)
    print(data.decode())

def tcplink()