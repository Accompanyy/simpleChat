#!/usr/bin/python
# coding:utf-8
from socket import *
from time import ctime
# from termios import tcflush,TCIFLUSH
import threading
import sys

HOST = '127.0.0.1'
PORT = 9999
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpCliSock = socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)
'''
因为每个客户端接收消息和发送消息是相互独立的，
所以这里将两者分开，开启两个线程处理
'''


def Send(sock, test):
    while True:
        try:
            data = input()
            sock.send(bytes(data,'utf-8'))
            if data == 'Quit':
                break
        except KeyboardInterrupt:
            sock.send(bytes('Quit', 'utf-8'))
            break


def Recv(sock, test):
    while True:
        data = sock.recv(BUFSIZ).decode('utf-8')
        if data == 'Quit.':
            print('He/She logout')
            continue
        if data == 'Quit':
            break
        print('%s' % data)


if __name__ == '__main__':
    print('Successful connection')
    while True:
        username = input('Your name(press only Enter to quit): ')
        tcpCliSock.send(bytes(username,'utf-8'))
        if not username:
            break
        # username is not None
        response = tcpCliSock.recv(BUFSIZ).decode('utf-8')
        if response == 'Reuse':
            print('The name is reuse, please set a new one')
            continue
        else:
            print('Welcome!')
            break

    if not username:
        tcpCliSock.close()

    recvMessage = threading.Thread(target=Recv, args=(tcpCliSock, None))
    sendMessage = threading.Thread(target=Send, args=(tcpCliSock, None))
    sendMessage.start()
    recvMessage.start()
    sendMessage.join()
    recvMessage.join()