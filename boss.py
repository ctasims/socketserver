import socket
import pdb

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect(('10.23.1.2', 8080))
s1.sendall("HELLO I'M 10.23.2.1 \n")
data = s1.recv(1024).strip().split()
print data

print 'Generate'
s1.sendall("GENERATE 32 BYTES CALLED 456 \n")
data = s1.recv(1024)
print data

print 'Goodbye 1'
s1.sendall("GOODBYE 10.23.1.2 \n")
s1.close()

print 'hello 2'
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect(('10.23.2.2', 8080))
s2.sendall("HELLO I'M 10.23.2.1 \n")
data = s2.recv(1024).strip().split()
print data

print '2, get stuff'
s2.sendall("GET 456 FROM 10.23.1.2 \n")
data = s2.recv(1024)
print data

print 'goodbye 2'
s2.sendall("GOODBYE 10.23.2.2 \n")
s2.close()
