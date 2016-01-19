import socket

test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

target = input("Ip address(only need the last，Please\n")
target = "192.168.1." + target

try:
    test.connect((target, 9999))
except Exception as e:
    print("address，Error")

wel = test.recv(1024).decode('utf-8')
print(wel)

while True:
    mes = input()

    if mes.lower() == "exit":
        test.send(b'exit')
        test.close()
        print("You have closed the connect successfully!")
        break

    data = mes.encode('utf-8')
    test.send(data)
    new = test.recv(1024).decode('utf-8')
    print(new)
