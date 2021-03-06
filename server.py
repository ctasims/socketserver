"""
Socket server for CS 485/585
Cianan Sims and Jason Rose

Server spawns new threads for incoming connects.
Maintains generated data in hashmap (dict)

Run server by typing 'python server.py' at bash

"""

import time
import thread
import sys
import socket
import subprocess
import tempfile
import pdb
import os

HOST = ''
PORT = 8080
db = {}

# Function for handling connections. Used to create threads.
def clientthread(conn):
    #conn.send('Welcome to the server. Type something and hit enter\n')
    data = conn.recv(1024).strip()
    if data == '':  # if they send nothing, close out
        conn.close()
        return
    greeted, client_ip = handshake(data)
    if greeted:
        # only accept more commands if they have manners!
        greeting = "HELLO %s I'M %s \n" % (client_ip, my_ip)
        conn.sendall(greeting)
        while 1:
            # Loop while client talks to us...
            data = conn.recv(1024).rstrip()
            if data == '':
                conn.close()
                return
            print data
            words = data.split()

            # Client says GENERATE...
            if len(words) == 5 and words[0] == 'GENERATE' and words[2] == 'BYTES' and words[3] == 'CALLED':
                byte_len = int(words[1])
                xyz = int(words[4])
                # calc the datum to store
                # xyz int is comprised of four bytes
                # get datum by repeating those four bytes and then summing them
                # not totally unique, but it'll work
                xyz_bytes = {}
                xyz_bytes[0] = (xyz & 0xff000000) >> 24
                xyz_bytes[1] = (xyz & 0x00ff0000) >> 16
                xyz_bytes[2] = (xyz & 0x0000ff00) >> 8
                xyz_bytes[3] = (xyz & 0x000000ff)
                datum = bytearray()
                datum.append('\x00')
                for num in range(byte_len):
                    index = num % 4
                    datum.append(xyz_bytes[index])
                db[xyz] = str(sum([int(bt) for bt in datum]))

                send_checksum(xyz, db[xyz], conn)

            # Client says GET...
            elif len(words) == 4 and words[0] == 'GET' and words[2] == 'FROM':
                xyz = int(words[1])
                get_ip = words[3]
                try:
                    socket.inet_aton(get_ip)  # check that their ip is legit
                except socket.error:
                    mean_goodbye(conn)

                # ip is legit
                their_datum = get_xyz(xyz, get_ip)
                if their_datum:
                    send_checksum(xyz, their_datum, conn)
                else:
                    say_goodbye(conn, client_ip)

            # Client says GIVE ME
            elif len(words) == 3 and words[0] == 'GIVE' and words[1] == 'ME':
                xyz = int(words[2])
                try:
                    reply = "%s is %s \n" % (xyz, db[xyz])
                    conn.sendall(reply)
                except KeyError:
                    mean_goodbye(conn)

            # Client says GOODBYE
            elif len(words) == 2:
                say_goodbye(conn, client_ip)
                return

            # if request is malformed
            else:
                say_goodbye(conn, client_ip)
                return

    else:
        print 'No greeting'
        say_goodbye(conn, client_ip)
        return

def send_checksum(xyz, datum, conn):
    """ generate the crc32 checksum of the datum and send it through the given
    connection

    """
    (fd, filename) = tempfile.mkstemp()  # use tempfile to store datum
    try:
        tfile = os.fdopen(fd, 'w')
        tfile.write(datum)
        tfile.close()
        proc = subprocess.Popen(['crc32', filename], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        time.sleep(0.2)
        checksum = proc.stdout.read()
        checksum.rstrip('\n')
        checksum = int(checksum, 16)
    finally:
        os.remove(filename)
    reply = "%s's CHECKSUM IS %s \n" % (xyz, checksum)
    conn.sendall(reply)

def get_xyz(xyz, ip):
    """ If client asks us to GET data from someone else, open a connection to
    the other server, greet them, and say GIVE ME XYZ

    """
    datum = ''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, 8080))
    greeting = "HELLO I'M %s \n" % my_ip
    client.send(greeting)
    response = client.recv(1024).strip()
    if response:
        msg = "GIVE ME %s \n" % xyz
        client.send(msg)
        response = client.recv(1024).split()
        # parse the response
        their_xyz = int(response[0])
        if their_xyz == xyz:
            datum = response[2]
        say_goodbye(client, ip)
    return datum


def say_goodbye(conn, their_ip):
    msg = "GOODBYE %s \n" % their_ip
    conn.send(msg)
    conn.close()
    return

def mean_goodbye(conn):
    msg = "ARE YOU FEELING LUCKY, PUNK? \n"
    conn.send(msg)
    conn.close()
    return

def handshake(msg):
    """ Check that client greets us courteously.

    """
    words = msg.split()
    try:
        ip = words[2]
        socket.inet_aton(ip)
        if words[0] == 'HELLO' and words[1] == "I'M":
            return True, ip
        else:
            return False, ''
    except socket.error:
        return False, ''
    except IndexError:
        return False, ''


""" ACTIVATE SERVER
create server socket and bind to it
"""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error, msg:
    print 'Bind failed.'
    sys.exit()

my_ip = socket.gethostbyname(socket.gethostname())

s.listen(10)  # queue up to 10 connections
print 'Socket listening'

# Accept client connections
while 1:
    # wait, accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    # start new threads takes 1st arg as function name to be run, second is tuple of args to function
    thread.start_new_thread(clientthread, (conn,))

s.shutdown()
s.close()

