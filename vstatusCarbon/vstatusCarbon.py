from daemon import Daemon
from plugins import plugins
from log import *
import config

from socket import socket
import time,platform

class vstatusCarbonDaemon(Daemon):
    def run(self):
	self.host=platform.node().split('.')[0]

	while True:
	    try:
		sock = socket()
		sock.connect( config.carbon )
		sock.sendall( '\n'.join(self.doit())+'\n')
		sock.close()
		LOGD('sent stats')
	    except Exception, e:
		LOGE(e)

            time.sleep(config.timeout)

    def doit(self):
	lines=[]
	now=int(time.time())

	for p in plugins:
	    try:
		lines.extend(p(self.host, now))
	    except Exception, e:
		print e
		LOGE(e)

	return lines


if __name__ == '__main__':
    v=vstatusCarbonDaemon('./dupa.pid')
    v.host='xeon'
    print v.doit()