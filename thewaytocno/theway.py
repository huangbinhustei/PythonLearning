import socket


test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


test.connect(('192.168.1.107', 9999))
wel = test.recv(1024).decode('utf-8')
print(wel)


while True:
	mes = input()
	
	if mes.lower() =="exit":
		test.send(b'exit')
		test.close()
		print("You have closed the connect successfully!")
		break

	data = mes.encode('utf-8')
	test.send(data)	
	new = test.recv(1024).decode('utf-8')
	print(new)


