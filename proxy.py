#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import sys


def handleRequest(tcpSocket, address):
    # recieving the packet from the accepted socket
    response = tcpSocket.recv(1024)
    # spliting its content in varialble, returning list of the strings
    first_line = response.split()
    # returns the utf-8 string in the 4 position into new variable
    address_name = str(first_line[4],"UTF-8")
    # check if the / is in the address and replaceing it with empty string
    replace = address_name.replace("/", "")
    #print the string
    print(address_name)
    try:
        #creating a new socket for the proxy, connecting it with the string address and the port of 80
        # and send the request message
        client_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connected")
        client_proxy.connect((address_name, 80))
        client_proxy.send(response)
        print("send")
        # recieve the send data from the client proxy check for the length and send it to the server
        # close the proxy and the server socket
        while True:
            data = client_proxy.recv(1024)
            if(len(data) > 0):
                tcpSocket.send(data)
            else:
                break    
        client_proxy.close()
        tcpSocket.close()
    except Exception as err:
        sys.exit(1)
        

def startServer(serverAddress, serverPort):
    # 1. Create server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 2. Bind the server socket to server address and server port
    s.bind(("127.0.0.1", serverPort))
    # 3. Continuously listen for connections to server socket
    while True:
        s.listen(10)
        clientsocket, address = s.accept()
        # 4. When a connection is accepted, call handleRequest function, passing new connection socket
        handleRequest(clientsocket, address)
    # 5. Close server socket
    s.close()


startServer("", 8005)
