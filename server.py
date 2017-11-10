#! /usr/bin/env python

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
from config import settings
import logging

def get_user(userfile):
	user_list = []
	with open(userfile) as f:
		for line in f:
			if not line.startswith('#') and line:
				if len(line.split()) == 4:
					user_list.append(line.split())
				else:
					print('error: users configuation')
	return user_list

def ftp_server():
	
	authorizer = DummyAuthorizer()

	user_list = get_user('./config/users.py')
	for user in user_list:
		name, passwd, permit, homedir = user
		try:
			authorizer.add_user(name, passwd, homedir, permit)
		except Exception as e:
			print(e)

	if settings.enable_anonymous == True:
		authorizer.add_anonymous(settings.anonymous_path)

	dtp_handler = ThrottledDTPHandler
	dtp_handler.read_limit = settings.max_download
	dtp_handler.write_limit = settings.max_upload

	handler = FTPHandler
	handler.authorizer = authorizer
	
	if settings.enable_logging == True:
		logging.basicConfig(filename=settings.loging_name, level=logging.INFO)

	handler.banner = settings.welcome_msg
	#handler.masquerade = '151.25.42.11'
	#handler.passive_ports = range(60000,65536)    

	handler.passive_ports = range(settings.passive_ports[0], settings.passive_ports[1])

	server = FTPServer((settings.ip, settings.port), handler)
    
	server.max_cons = settings.max_cons
	server.max_cons_per_ip = settings.max_per_ip
    
	print('starting FTP server...')
	server.serve_forever()

if __name__ == "__main__":
    ftp_server()
