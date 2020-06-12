#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import sys


def handleRequest(tcpSocket):
    try:
	    # 1. Receive request message from the client on connection socket
	    request = tcpSocket.recv(1024).decode()
	    # 2. Extract the path of the requested object from the message (second part of the HTTP header)
	    file_requested = request.split(' ')[1]
	    file_path = file_requested
	    # 3. Read the corresponding file from disk
	    f = open(file_path[1:])
	    response_data = f.read()
	    tcpSocket.send('HTTP/1.1 200 OK \r\n\r\n'.encode())
	    # 4. Store in temporary buffer
	    for i in range(0, len(response_data)):
		    tcpSocket.send(response_data[i].encode())
	    # 7. Close the connection socket
	    tcpSocket.close()
		# 5. Send the correct HTTP response error
    except IOError:
        tcpSocket.send("HTTP/1.1 200 OK \r\n\r\n 404 Not Found".encode())
    tcpSocket.close()
	    

def startServer(serverAddress, serverPort):
	# 1. Create server socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 2. Bind the server socket to server address and server port
	s.bind(("127.0.0.1", serverPort))
	# 3. Continuously listen for connections to server socket
	s.listen(5)
	while True:
		(clientsocket, address) = s.accept()
		handleRequest(clientsocket)
	# 4. When a connection is accepted, call handleRequest function, passing new connection socket (see https://docs.python.org/3/library/socket.html#socket.socket.accept)
	s.close()
	# 5. Close server socket
	pass # Remove/replace when function is complete


startServer("", 8035)