#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select
import binascii
import math

ICMP_ECHO_REQUEST = 8   #ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0 #ICMP type code for echo reply messages
ICMP_CODE = socket.getprotobyname('icmp')

def checksum(string): 
	csum = 0
	countTo = (len(string) // 2) * 2  
	count = 0

	while count < countTo:
		thisVal = string[count+1] * 256 + string[count]
		csum = csum + thisVal 
		csum = csum & 0xffffffff  
		count = count + 2
	
	if countTo < len(string):
		csum = csum + string[len(string) - 1]
		csum = csum & 0xffffffff 
	
	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum 
	answer = answer & 0xffff 
	answer = answer >> 8 | (answer << 8 & 0xff00)

	return answer

"""
Method, that creates the header of the packet and 
structure the packet with the echo messege
"""
def create_packet(id):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = ''
    my_checksum = checksum(header + data.encode('utf-8'))
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0,
            socket.htons(my_checksum), id, 1)
    return header + data.encode('utf-8')

def sendOnePing(icmpSocket, destinationAddress, ID):
	 
    destinationAddress  =  socket.gethostbyname(destinationAddress)
    my_checksum = 0
    #creating an empty header
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    data = ''
    data = struct.pack("d", time.time()) + data
    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)
     # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data.encode('utf-8')
    icmpSocket.sendto(packet, (destinationAddress, 0))


def recieveOnePing(icmpSocket, ID, sendTime, timeout):
    time_left = timeout
    #checking for the recieved packet, unpack the message and declare the time between them/delay
    while True:
        #the started time
        started = time.time()
        ready = select.select([icmpSocket], [], [], time_left)
        howLong = time.time() - started
        if ready[0] == []: # if the packet is empty do a timeout
            return 0
        time_received = time.time()
        rec_packet, addr = icmpSocket.recvfrom(1024)
        # The last 8 bytes are the header of the packet we sent to the server
        icmp_header = rec_packet[-8:]
        type, code, checksum, p_id, sequence = struct.unpack(
                'bbHHh', icmp_header)
        if p_id == ID:
            #check for the if the icmp id match the packet id
            total_time_ms = (time_received - sendTime) * 1000
            # Round to 3 decimal places:
            total_time_ms = math.ceil(total_time_ms * 1000) / 1000
            return (addr[0], total_time_ms)
        time_left -= time_received - sendTime
        if time_left <= 0:
            return 0

"""
Method creating a socket
goes thrue all the packets and returns the ping between them
"""
def doOnePing(destinationAddress, ttl, timeout =3 ):
    #creating socket
    tracerouteSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)
    tracerouteSocket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

    #declaring a id for the packets and create a packet
    packet_id = int(1024)
    packet = create_packet(packet_id)

    #goes to every packet and send the information to the destinationAddress
    while packet:
        sent = tracerouteSocket.sendto(packet, (destinationAddress, 1))
        packet = packet[sent:]
    
    #the returned ping from the recive will be stored in this variable
    ping_res = recieveOnePing(tracerouteSocket, packet_id, time.time(), timeout)
    tracerouteSocket.close()
    #returns the ping
    return ping_res

"""
Run three time the doOnePing in order to check for the right ping
saving the resulted pings into a string
and returns the final string with the address
"""
def doThreeDelay(destinationAddress, ttl):
    #do 3 pings
    first = doOnePing(destinationAddress, ttl)
    second = doOnePing(destinationAddress, ttl)
    third = doOnePing(destinationAddress, ttl)

    #checks if thre is a empty return or store the result into a string
    if first == 0:
        firststr = '*'
    else:
        firststr = first[0] + ' - ' + str(first[1]) + ' ms'
    if second == 0:
        secondstr = ' '
    else:
        secondstr = second[0] + ' - ' + str(second[1]) + ' ms'
    if third == 0:
        thirdstr = '*'
    else:
        thirdstr = third[0] + ' - ' + str(third[1]) + ' ms'

    final_string = firststr + ', ' + secondstr + ', ' + thirdstr
    final_string = str(ttl) + '  ' + final_string

    # check if the destinationAddress is reached 
    if first == 0:
        destination_reached = False
    else:
        destination_reached = first[0] == destinationAddress
    #returns the final string from the 3 pings and the address
    return (final_string, destination_reached)
"""
Main method, which prints the final result in traceroute format
"""
def ping(host, timeout=3):
    #a main method to print the final resul with ttl of max 30
    max_ttl = 30
    dest_addr = socket.gethostbyname(host)
    print('myTraceRoute to ' + host + ' (' + dest_addr + '), ' + str(max_ttl) +
      ' hops max.')
    try:
        
        for x in range(1, max_ttl+1):
            (line, destination_reached) = doThreeDelay(dest_addr, x)
            print(line)
            if destination_reached:
                break
    except Exception as err:
        print(err)
    except KeyboardInterrupt as err:
        print(err)
       
 
	
ping("lancaster.ac.uk")

