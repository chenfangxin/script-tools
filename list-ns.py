#!/usr/bin/python

import os
import fnmatch

if os.geteuid() != 0:
	print "This cript must be run as root\n"
	exit(1)

def getinode(pid, type):
	link = '/proc/' + pid + '/ns/' + type
	ret = ''
	# print link
	try:
		ret = os.readlink(link)
		# print ret
	except OSError as e:
		ret=''
		pass
	return ret

def getcmd(p):
	try:
		cmd = open(os.path.join('/proc', p, 'cmdline'),'rb').read()
		if cmd=='':
			cmd = open(os.path.join('/proc', p, 'comm'),'rb').read()
		cmd = cmd.replace('\x00', ' ')
		cmd = cmd.replace('\n', ' ')
		return cmd
	except:
		return ''

def getpcmd(p):
	try:
		f = '/proc/' + p + '/stat'
		arr = open(f, 'rb').read().split()
		cmd = getcmd(arr[3])
		if cmd.startswitch('/usr/bin/docker'):
			return 'docker'
	except:
		pass
	return ''

nslist = os.listdir('/proc/1/ns/')
if len(nslist)==0:
	print 'No Namespace found for PID=1'
	exit(1)

baseinode=[]
for x in nslist:
	baseinode.append(getinode('1', x))

print baseinode

err=0
ns=[]
ipnlist=[]

try:
	netns = os.listdir('/var/run/netns')
	for p in netns:
		fd = os.open('/var/run/netns/' + p, os.O_RDONLY)
		info = os.fstat(fd)
		os.close(fd)
		ns.append('--net:[' + str(info.st_ino) + '] created by ip netns add ' + p)
		ipnlist.append('net:[' + str(info.st_ino) + ']')
except:
	pass

pidlist = fnmatch.filter(os.listdir('/proc/'), '[0123456789]*')
# print pidlist
for p in pidlist:
	try:
		pnlist = os.listdir('/proc/' + p + '/ns/');
		# print pnlist
		for x in pnlist:
			# print p, x
			i = getinode(p, x)
			if i!='' and i not in baseinode:
				# print i, p
				cmd = getcmd(p)
				pcmd = getpcmd(p)
				if pcmd != '':
					cmd = '[' + pcmd + ']' + cmd
					tag = ''

				if i in ipnlist:
					tag = '**'
				ns.append(p + ' ' + i + tag + ' ' + cmd)
	except:
		pass

print '{0:10} {1:20} {2}'.format('PID', 'Namespace', 'Thread/Command')
for e in ns:
	x = e.split(' ', 2)
	print '{0:10} {1:20} {2}'.format(x[0], x[1], x[2][:60])
