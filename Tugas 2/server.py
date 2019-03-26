# Import module
from socket import *
import socket
import threading
import sys
import os
import time

class ProcessTheClient(threading.Thread):
	def __init__(self, connection, address):
		self.connection = connection
		self.address = address
		threading.Thread.__init__(self)

	def run(self):
		file = open('file.jpg', 'rb')
		data = file.read()
		while True:
			print "now sending", self.address
			sent = 0
			for x in data:
				self.connection.sendto(x, self.address)
				sent+=1
			print "done sending", self.address
			size = os.stat('file.jpg').st_size
			print "\r sent {} of {} " . format(sent, size)
			time.sleep(10)

class Server(threading.Thread):
	def __init__(self):
		self.the_clients = []
		self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		threading.Thread.__init__(self)

	def run(self):
		host = socket.gethostname()
		port = 9000
		self.my_socket.bind((host, port))
		while True:
			data, self.client_address = self.my_socket.recvfrom(1024)
			print >> sys.stderr, 'connection from', self.client_address

			clt = ProcessTheClient(self.my_socket, self.client_address)
			clt.start()

			self.the_clients.append(clt)

def main():
	svr = Server()
	svr.start()

if __name__=="__main__":
	main()
