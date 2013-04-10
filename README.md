socketserver
============
Cianan Sims and Jason Rose
CS 585
2012 Fall

Create a server in python for use in the class-wide network.
Server code is in server.py
Client.py is an old client (ignore it).
boss.py is our script for running the GENERATE and GET commands for Types 2 and 3.
Servers are run on the two endpoints. The router sends them GENERATE and GET commands.
For GET, one endpoint queries the other for data, which is then GENERATEd and returned.
