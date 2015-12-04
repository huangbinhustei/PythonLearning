import socket
import threading
import time
import four_arithmetic_operation
calc = four_arithmetic_operation.main

svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
svr.bind(("127.0.0.1", 9999))
svr.listen(5)
print("Waiting for connection....")


def tcp_link(me_socket, this_client):
    print("someone come in! %s:%s" % this_client)
    me_socket.send(b'Welcome!')
    while True:
        data = me_socket.recv(1024).decode('utf-8')
        time.sleep(1)
        if not data or data == 'exit':
            break
        me_ans = calc(data)
        me_socket.send(('hello,%s' % me_ans).encode('utf-8'))
    me_socket.close()
    print('closed')


while True:
    sock, cli = svr.accept()
    t = threading.Thread(args=(sock, cli), target=tcp_link)
    t.start()
