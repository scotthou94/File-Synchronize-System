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

def download_all(location, path=''):
	print 'download_all:'
	print location+path
	rootdir = []
	ftp.retrlines('MLSD '+path, rootdir.append)

	print 'download_all: rootdir = ', rootdir
	for line in rootdir:
		file = line.split(';')[5][1:]
		if file == '.DS_Store':
			continue
		#print file
		if line.split(';')[3] == 'type=file':
			print 'download %s' % path+'/'+file
			ftp.retrbinary('RETR '+path+'/'+file, open(location+path+'/'+file, 'wb').write)
		else:
			if os.path.exists(location+path+'/'+file) == False:
				os.mkdir(location+path+'/'+file)
				print 'make local directory %s' % location+path+'/'+file
			download_all(location, path+'/'+file)


#def upload_dir(location, dir):


def rm_dir(dir):
	try:
		ftp.rmd(dir)
	except:
		files = []
		ftp.retrlines('MLSD '+dir, files.append)
		for line in files:
			file = line.split(';')[5][1:]
			if line.split(';')[3] == 'type=file':
				ftp.delete(dir+'/'+file)
			else:
				rm_dir(dir+'/'+file)
		ftp.rmd(dir)



def check_update(last_sync, path, location):
	new_files = []
	del_files = []
	cloud_files = []
	files = []
	ret = []
	dir = ''

	#print path
	files = os.listdir(location + path)
	cloud_files = ftp.nlst('/'+path)
	
	for file in files:
		#print location+path+file
		if file == '.DS_Store':
			continue
		if os.stat(location + path + file).st_mtime <= last_sync:
			if file in cloud_files:
				continue
			if os.path.isfile(location+path+file) == True:
				new_files.append(path+file)
			else:
				print path
				print cloud_files
				print file
				ftp.mkd('/' + path + file)
				new_files.extend(check_update(last_sync, path+file+'/', location))
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
						#print 'find'
						if os.path.isfile(location + path + file + '/' + new_file) == True:
							new_files.append(path + file + '/' + new_file)
						else:
							ftp.mkd('/' + path + file + '/' + new_file)
							new_files.extend(check_update(last_sync, path + file + '/' + new_file+'/', location))
			dir = file + '/'
			new_files.extend(check_update(last_sync, path + dir, location))
			#print check_update(last_sync, path + dir, location, ftp)
		else:
			continue

	return new_files

def check_update_del(path, location):
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
			del_files.extend(check_update_del(path+'/'+file, location))

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
	while (login):
		user = raw_input('please enter username: ')
		password = raw_input('please enter password: ')
		try:
			ftp.connect('127.0.0.1', 2121)
			ftp.login(user, password)
			ftp.set_pasv(False)
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
	ftp.connect('127.0.0.1', 2121)
	ftp.login('test', 'test')
	ftp.set_pasv(False)
	'''

	rootdir = ftp.nlst('/')
	#print rootdir
	if len(rootdir) == 1 and rootdir[0] == '.DS_Store':
		print 'No data in cloud'
	elif len(rootdir) > 0:
		print 'There is existing content in cloud'
		print 'Do you want to overwrite cloud content? (y/n)'
		while(True):
			answer = raw_input('')
			if answer == 'y' or answer == 'Y':
				print 'overwriting...'
				break
			elif answer == 'n' or answer == 'N':
				download_all('./test')
				break
			else:
				print 'Please enter y or n'
	ftp.quit()
	

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
		#print os.stat('./test').st_mtime
		#print last_sync
		if os.stat('./test').st_mtime > last_sync:
			#print 'check'
			cloud_files = ftp.nlst('/')
			local_files = os.listdir('./test/')
			for new_file in local_files:
				if new_file not in cloud_files:
					if os.path.isfile('./test/' + new_file) == True:
						new_files.append(new_file)
					else:
						ftp.mkd('/' + new_file)
						new_files.extend(check_update(last_sync, new_file+'/', './test/'))

			

		new_files.extend(check_update(last_sync, '', './test/'))
		del_files.extend(check_update_del('', './test/'))

		new_files = list(set(new_files))
		
		if len(new_files) > 0 or len(del_files) > 0:
			ftp.cwd('/')
			print 'need update:'
			for file in new_files:
				if os.path.isfile('./test/' + file) == True:
					upload('./test/', file)
				#else:
				#	upload_dir('./test/', file)
			
			for file in del_files:
				print 'delete %s' % file
				'''
				if os.path.isfile(file) == True:
					print file+' is a file'
					ftp.delete(file)
				else:
					print file+' is a dir'
					rm_dir(file)
				'''
				try:
					rm_dir(file)
				except:
					ftp.delete(file)
			
		else:
			print 'up to date [%f]' % time.time()

		last_sync = time.time()
		ftp.quit()
		#break
		time.sleep(2)
