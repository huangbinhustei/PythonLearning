import socket

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# test.connect(('www.163.com', 80))
# test.send(b'GET /HTTP/1.1\r\nHost:www.sina.com.cn\r\nConnection:close\r\n\r\n')
# print(1)
# buffer = []
# while True:
#     d = test.recv(1024)
#     print(2)
#     if d:
#         print(3)
#         buffer.append(d)
#     else:
#         print(4)
#         break
# data = b''.join(buffer)
#
# header, html = data.split(b'\r\n\r\n', 1)
# print(header.decode('utf-8'))
# print(html)


test.connect(('127.0.0.1', 9999))
print("connect!")
wel = test.recv(1024).decode('utf-8')
print(wel)

mes = input()
data = mes.encode('utf-8')
test.send(data)

new = test.recv(1024).decode('utf-8')
print(new)

w8 = input("press any key to close\n")
test.send(b'exit')
test.close()



