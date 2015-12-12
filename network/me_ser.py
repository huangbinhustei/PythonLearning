import socket
import threading
import time
from datetime import datetime
moment = datetime.now
import logging
logging.basicConfig(level=logging.INFO)
import sys
sys.path.append("..")
import four_arithmetic_operation
calc = four_arithmetic_operation.main

localIP = socket.gethostbyname(socket.gethostname())

svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
svr.bind(("", 9999))
svr.listen(5)
logging.info("Start service！\tTime = " + str(moment())[:19] + "\tLocal IP = " + localIP)


def tcp_link(me_socket, this_client):
    logging.info("Establish connection！\tClient = " + str(this_client) + "\tTime = " + str(moment())[:19])
    me_socket.send(b'Welcome!')
    while True:
        data = me_socket.recv(1024).decode('utf-8')
        time.sleep(1)
        start = moment()
        if not data or data == 'exit':
            break
        try:
            me_ans = calc(data)
            time_cast = str(moment()-start)
            logging.info("Correct input！\tClient = " + str(this_client) + "\tTime = " + str(moment())[:19])
            mes = "Hello,by cal in " + time_cast + ",the answer is：\n" + str(me_ans)
            me_socket.send(mes.encode('utf-8'))
        except BaseException as e:
            logging.error("Format error！\tClient = " + str(this_client) + "\tTime = " + str(moment())[:19])
            me_socket.send("Format error!".encode('utf-8'))

    me_socket.close()
    logging.info("Close connect！\tClient = " + str(this_client) + "\tTime = " + str(moment())[:19])


while True:
    sock, cli = svr.accept()
    t = threading.Thread(args=(sock, cli), target=tcp_link)
    t.start()
