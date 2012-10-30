# echo server program
import thread
import sys
import socket
import zlib
import pdb
import os

HOST = ''
PORT = 8080
db = {}
my_ip = '10.23.1.2'

# Function for handling connections. Used to create threads.
def clientthread(conn):
    #conn.send('Welcome to the server. Type something and hit enter\n')
    data = conn.recv(1024).strip()
    greeted, client_ip = handshake(data)
    if greeted:
        greeting = "HELLO " + client_ip + " I'M " + my_ip + "\n"
        conn.sendall(greeting)
        while 1:
            # Loop while client talks to us...
            data = conn.recv(1024).strip()
            words = data.split()

            # Client says GENERATE...
            if len(words) == 5 and words[0] == 'GENERATE' and words[2] == 'BYTES' and words[3] == 'CALLED':
                byte_len = int(words[1])
                xyz = int(words[4])
                # calc the datum to store
                # xyz int is comprised of four bytes
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
                # db[xyz] = zlib.crc32(datum)

        # Client says GET...
            elif len(words) == 4 and words[0] == 'GET' and words[2] == 'FROM':
                xyz = int(words[1])
                get_ip = words[3]
                try:
                    socket.inet_aton(get_ip)
                except socket.error:
                    mean_goodbye()
                # ip is legit

                their_datum = get_xyz(xyz, get_ip)
                if datum:
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
                    punk_msg = "ARE YOU FEELING LUCKY, PUNK? \n"
                    conn.send(punk_msg)
                    say_goodbye(conn, client_ip)

                # Client says GOODBYE
            elif len(words) == 2:
                say_goodbye(conn, client_ip)

                # if request is malformed
            else:
                say_goodbye(conn, client_ip)

    else:
        print 'No greeting'
        say_goodbye(conn, client_ip)

def send_checksum(xyz, datum, conn):
    reply = "%s's CHECKSUM IS %s \n" % (xyz, zlib.crc32(str(datum)))
    conn.sendall(reply)

def get_xyz(xyz, ip):
    """
    """
    datum = ''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, 8080))
    greeting = "HELLO " + ip + " I'M " + my_ip + "\n"
    client.send(greeting)
    response = s.recv(1024)
    responded, their_ip = handshake(response)
    if responded:
        msg = "GIVE ME " + xyz + " \n"
        client.send(msg)
        response = s.recv(1024).split()
        # parse the response
        if response[0] == xyz:
            datum = response[2]
        say_goodbye(client, ip)
    return datum


def say_goodbye(conn, their_ip):
    msg = "GOODBYE %s \n" % their_ip
    conn.send(msg)
    conn.close()


def handshake(msg):
    words = msg.split()
    print 'Handshake: %s' % words
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


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error, msg:
    print 'Bind failed.'
    sys.exit()

s.listen(10)
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

