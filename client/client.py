from ftplib import FTP
import os
import time



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
	del_files = []
	files = []
	ret = []
	dir = ''

	#print path
	files = os.listdir(location + path)
	for file in files:
		#print location+path+file
		if file == '.DS_Store':
			continue
		if os.stat(location + path + file).st_mtime <= last_sync:
			continue
		if os.path.isfile(location + path + file) == True:
			#new_files.append(location + path + file)
			new_files.append(path + file)
		elif os.path.isdir(location + path + file) == True:
			#print path+file
			new = False
			try:
				ftp.cwd('/' + path + file)
			except:
				print 'create /%s in server' % (path+file)
				ftp.mkd('/' + path + file)
				new = True
			if new == False:
				cloud_files = ftp.nlst()
				local_files = os.listdir(location + path + file)
				for new_file in local_files:
					if new_file not in cloud_files:
						new_files.append(path + file + '/' + new_file)
				
			dir = file + '/'
			new_files.extend(check_update(last_sync, path + dir, location, ftp))
			#print check_update(last_sync, path + dir, location, ftp)
		else:
			continue

	return new_files

def check_update_del(path, location, ftp):
	del_files = []
	files = []
	dir = ''

	ftp.cwd('/' + path)
	cloud_files = ftp.nlst()
	local_files = os.listdir(location + path)

	for file in cloud_files:
		#print path+'/'+file
		#print location + path + '/' + file
		if file not in local_files:
			del_files.append(path + '/' +file)
		
		elif os.path.isdir(location + path + '/' + file) == True:
			#print 'go to check %s' % path+file
			del_files.extend(check_update_del(path+'/'+file, location, ftp))

	return del_files



if __name__ == '__main__':

	ftp = FTP()
	timeout = 30
	port = 2121
	address = '34.237.249.39'

	new_files = []
	timestamp = {}
	last_sync = 0.0
	login = True

	#initial login
	'''
	while (login):
		user = raw_input('please enter username: ')
		password = raw_input('please enter password: ')
		try:
			ftp.connect('127.0.0.1', 2121)
			ftp.login(user, password)
			login = False
		except:
			print 'login refused!'
			login = True

	print 'please enter the directory to backup(e.g. ./test):'
	directory = os.path.split(raw_input(''))[1]
	try:
		ftp.cwd(directory)
	except:
		print 'create directory in server'
		ftp.mkd('/' + directory)
	'''

	while (True):
		new_files = []
		del_files = []
		'''
		if connect(ftp) == False:
			print 'connection refused'
			break
		'''
		ftp.connect('127.0.0.1', 2121)
		ftp.login('test', 'test')

		print ''
		print os.stat('./test').st_mtime
		print last_sync
		if os.stat('./test').st_mtime > last_sync:
			print 'check'
			cloud_files = ftp.nlst('/')
			local_files = os.listdir('./test/')
			for new_file in local_files:
				if new_file not in cloud_files:
					new_files.append(new_file)
			'''
			for del_file in cloud_files:
				if del_file not in local_files:
					del_files.append(del_file)
			'''
			

		new_files.extend(check_update(last_sync, '', './test/', ftp))
		del_files.extend(check_update_del('', './test/', ftp))

		
		if len(new_files) > 0 or len(del_files) > 0:
			ftp.cwd('/')
			print 'need update:'
			for file in new_files:
				upload('./test/', file)
			
			for file in del_files:
				print 'delete %s' % file
				ftp.delete(file)
			
		else:
			print 'up to date'

		last_sync = time.time()
		ftp.quit()
		#break
		time.sleep(5)
