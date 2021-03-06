#!/usr/bin/python
# coding:utf-8
from socket import *
from time import ctime
import threading
import re

HOST = ''
PORT = 9999
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

clients = {}  # username -> socket
chatwith = {}  # user1.socket -> user2.socket


# clients字典中记录了连接的客户端的用户名和套接字的对应关系
# chatwith字典中记录了通信双方的套接字的对应

# messageTransform()处理客户端确定用户名之后发送的文本
# 文本只有四种类型：
#	None
#   Quit
#	To:someone
#	其他文本
def messageTransform(sock, user):
    while True:
        data = sock.recv(BUFSIZ)
        if not data:
            if sock in chatwith:
                chatwith[sock].send(data)
                del chatwith[chatwith[sock]]
                del chatwith[sock]
            del clients[user]
            sock.close()
            break

        if data.decode('utf-8') == 'Quit':
            sock.send(data)
            if sock in chatwith:
                data = '%s.' % data.decode('utf-8')
                chatwith[sock].send(bytes(data, 'utf-8'))
                del chatwith[chatwith[sock]]
                del chatwith[sock]
            del clients[user]
            sock.close()
            break
        elif re.match('^To:.+', data.decode('utf-8')) is not None:
            data = data.decode('utf-8')[3:]
            if data in clients:
                if data == user:
                    sock.send(bytes('Please don\'t try to talk with yourself.', 'utf-8'))
                else:
                    chatwith[sock] = clients[data]
                    chatwith[clients[data]] = sock
            else:
                sock.send(bytes('the user %s is not exist' % data, 'utf-8'))
        elif data.decode('utf-8') == 'Users':
            s = ''
            i = 1
            for clnt in clients.keys():
                s += f"{i}: {clnt} \n"
                i += 1
            sock.send(bytes(s, 'utf-8'))
        else:
            if sock in chatwith:
                chatwith[sock].send(bytes('[%s] %s: (%s)' % (ctime(), user, data.decode('utf-8')), 'utf-8'))
            else:
                sock.send(
                    bytes('Nobody is chating with you. Maybe the one talked with you is talking with someone else',
                          'utf-8'))


# 每个客户端连接之后，都会启动一个新线程
# 连接成功后需要输入用户名
# 输入的用户名可能会：
#	已存在
#	(客户端直接输入ctrl+c退出)
#	合法用户名
def connectThread(sock, test):  # client's socket

    user = None
    while True:  # receive the username
        username = sock.recv(BUFSIZ)
        if not username:  # the client logout without input a name
            print('The client logout without input a name')
            break
        username = username.decode('utf-8')
        if username in clients:  # username existed
            sock.send(bytes('Reuse', 'utf-8'))
        else:  # correct username
            sock.send(bytes('OK', 'utf-8'))
            clients[username] = sock  # username -> socket
            user = username
            break
    if not user:
        sock.close()
        return
    print('The username is: %s' % user)
    # get the correct username

    messageTransform(sock, user)


if __name__ == '__main__':
    while True:
        print('...WAITING FOR CONNECTION')
        tcpCliSock, addr = tcpSerSock.accept()
        print('CONNECTED FROM: ', addr)
        chat = threading.Thread(target=connectThread, args=(tcpCliSock, None))
        chat.start()
