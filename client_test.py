#! /usr/bin/env python

from ftplib import FTP  
      
ftp = FTP()  
timeout = 30  
port = 2121  
pub_address = '54.145.165.176'
loc_address = '127.0.0.1'
ftp.connect(pub_address, port)  
ftp.login('root','root')   
print ftp.getwelcome()    
print ftp.dir()
ftp.quit()
