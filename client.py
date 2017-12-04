from ftplib import FTP
import os
import time


def connect(ftp):
	try:
		ftp.connect('127.0.0.1', 2121)
		ftp.login('test', 'test')
	except:
		return False
	return True

def upload(location, file):
	try:
		ftp.storbinary('STOR '+file, open(location+file, 'rb'))
	except:
		print 'upload failed %s' % file
		return False
	print 'upload %s' % file
	return True

def check_update(last_sync, path, location, ftp):
	new_files = []
	files = []
	dir = ''

	#print path
	files = os.listdir(location + path)
	for file in files:
		#print location+path+file
		if os.stat(location + path + file).st_mtime <= last_sync:
			continue
		if os.path.isfile(location + path + file) == True:
			#new_files.append(location + path + file)
			new_files.append(path + file)
		elif os.path.isdir(location + path + file) == True:
			#print path+file
			try:
				ftp.cwd('/' + path + file)
			except:
				print 'create /%s in server' % (path+file)
				ftp.mkd('/' + path + file)
			dir = file + '/'
			new_files.extend(check_update(last_sync, path + dir, location, ftp))
		else:
			continue


	return new_files


if __name__ == '__main__':

	ftp = FTP()
	timeout = 30
	port = 2121
	address = '34.237.249.39'

	new_files = []
	timestamp = {}
	last_sync = 0.0

	while (True):
		'''
		if connect(ftp) == False:
			print 'connection refused'
			break
		'''
		ftp.connect('127.0.0.1', 2121)
		ftp.login('test', 'test')
		new_files = check_update(last_sync, '', './test/', ftp)
		
		#ftp.dir()
		ftp.cwd('/')
		for file in new_files:
			print file
			upload('./test/', file)
		last_sync = time.time()
		#ftp.quit()
		break
