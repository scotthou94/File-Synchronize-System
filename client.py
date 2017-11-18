#！/usr/bin/env python

from ftplib import FTP  

ftp = FTP()
timeout = 30
port = 2121
address = '127.0.0.1'

def connect():
	try:
		ftp.connect(address, port)
		ftp.login('root', 'root')
	except:
		return False
	return True

def upload(path, filename):
	try:
		ftp.storbinary('STOR '+path+filename, open(path+filename, 'rb'))
	except:
		return False
	return True


if __name__ == '__main__':

	files = []
	timestamp = {}
	last_sync = 0.0

	connect()
	ftp.connect(address, port)
	ftp.login('root', 'root')