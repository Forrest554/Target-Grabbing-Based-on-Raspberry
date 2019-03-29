import socket
import threading

ip_port = ('127.0.0.1',9998)
sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,0)
sk.bind(ip_port)



def listen():
	global data
	while True:
		data = sk.recv(1024)
data = ''
t = threading.Thread(target = listen, args = ())
t.start()
a = 0
while True:
	a += 1
	if a == 5000:
		a = 0
	if data.lower() != '':
		s = str(data, encoding = "utf8")
		print(data, s)
		print(s.split('&'))
		data = ''