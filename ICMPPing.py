#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select
import binascii  


ICMP_ECHO_REQUEST = 8 #ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0 #ICMP type code for echo reply messages


    
def checksum(str_):
    sum = 0
    countTo = (len(str_)/2)*2
    count = 0
    while count<countTo:
        thisVal = str_[count + 1]*256 + str_[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2

    if countTo<len(str_):
        sum = sum + str_[len(source_string) - 1]
        sum = sum & 0xffffffff 

    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff


    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer
"""
Method. which returns the delay between the packets
unpacks the send packet and check for equal codes
then returns the delay
"""
def receiveOnePing(icmpSocket, destinationAddress, ID, timeout):
    
    left = timeout
    #checking for the recieved packet, unpack the message and declare the time between them/delay
    while True:
        #the started time
        started = time.time()
        ready = select.select([icmpSocket], [], [], left)
        howLong = (time.time() - started)
         # if the packet is empty do a timeout
        if ready[0] == []:
            return

        recieved = time.time()
        recPacket, addr = icmpSocket.recvfrom(1024)
        # The first 20 and last 28 bytes are the header of the packet we sent to the server
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )
        if type != 8 and packetID == ID:
            #check for the if the icmp id match the packet id
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return recieved - timeSent

        left = left - howLong
        if left <= 0:
            return

"""
Method, that creates the header of the packet and 
structure the packet with the echo messege
"""
def sendOnePing(icmpSocket, destinationAddress, ID):
	 
    destinationAddress  =  socket.gethostbyname(destinationAddress)
    my_checksum = 0
    #creating an empty header
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1) 
    padding = 192  * "Q"
    data = struct.pack("d", time.time()) + padding.encode()
    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)
     # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data
    icmpSocket.sendto(packet, (destinationAddress, 0))
	
"""
Method creating a icmp socket and executing sendOnePing and RecieveOnePing
and save the result in variable ping
where the output is the ping between the messeges
"""
def doOnePing(destinationAddress, timeout): 
	
    icmp = socket.getprotobyname("icmp")
    try:
        #creating an icmp socket
        icmpsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except PermissionError as e:
        e.args = (e.args if e.args else tuple()) + ((
            " -ICMP messages can only be sent from processes"
            " running as root."
        ),)
        raise
        

    my_ID = os.getpid() & 0xFFFF
    #executing the send method and saving the return from the recieve in a variable
    sendOnePing(icmpsocket, destinationAddress, my_ID)
    ping = receiveOnePing(icmpsocket,destinationAddress, my_ID, timeout)
    #closing the icmp socket
    icmpsocket.close()
    #returning the current ping
    return ping
	
"""
    Main method taking two parameters for host address and timeout
    prints the ping in milliseconds every 1 second
"""
def ping(host, timeout=1):
    #Main method that goes to loop and printing the delay every 1 second
    while True:
        time.sleep(1)
        print('host: {}'.format(host))
        delay = doOnePing(host, timeout)
        if delay is None:
            print('failed. (Timeout within {} seconds.)'.format(timeout))
        else:
            delay = round(delay * 1000.0, 4)
            print('ping is: {} milliseconds.'.format(delay))
       
 
	#calling the prinr method with the address of lancaster.ac.uk
ping("lancaster.ac.uk")

