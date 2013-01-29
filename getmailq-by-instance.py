#!/usr/bin/python -d
# getmailq-by-instance.py - written by Tyzhnenko Dmitry 2013. Steal and share.
# Get postfix instances queue lengths and extend SNMP OID

import sys
import os
import re 
from subprocess import call


__version__ = '2.0'


#Place in /usr/local/bin/
#pass .1.3.6.1.4.1.2021.54 postfix-instance-mailq /usr/local/bin/getmailq-by-instance.py .1.3.6.1.4.1.2021.55


DATA={}
BASE=sys.argv[1]
REQ_T=sys.argv[2]
REQ=sys.argv[3]

def sort_nicely( l ): 
  """ Sort the given list in the way that humans expect. 
  """ 
  convert = lambda text: int(text) if text.isdigit() else text 
  alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
  l.sort( key=alphanum_key ) 

def count_queue(queue_dir):
	COUNT = os.popen("find %s/ -type f | wc -l" % (queue_dir) ).read()
	return COUNT

def get_data(oid):
	global DATA
	data = DATA[str(oid)]
	if type(data) == dict :
		count = count_queue("%s/%s/" % ( data["instance"], data["queue"] ))
		new_data = "%s\ninteger\n%i" % (oid,int(count))
		return new_data
	else:
		return data

def main():
	global DATA
	global BASE
	global REQ_T
	global REQ
	POSTCONF="/usr/sbin/postconf"
	QUEUES = { 1: "deferred", 2: "active", 3: "incoming", 4: "hold" }
	INSTANCES_CONFS=os.popen(POSTCONF +  ' -h multi_instance_directories').read().split()
	inst_path = os.popen(POSTCONF + ' -h  queue_directory').read().split()
	inst_num=10
	
	INSTANCES_Q_DIRS = { inst_num : inst_path[0]}
	inst_num=20

	for conf_d in INSTANCES_CONFS:
		INSTANCES_Q_DIRS[inst_num] = os.popen(POSTCONF + ' -c ' + conf_d + ' -h queue_directory').read().split()[0]
		inst_num = inst_num + 10

	#print INSTANCES_Q_DIRS
	#sys.exit(1)

	#q_num=1
	
	for key in INSTANCES_Q_DIRS:
		instance = INSTANCES_Q_DIRS[key]
		inst_name = os.path.basename(instance)
		DATA["%s.1.%i" % (BASE, key)] = "%s.1.%i\ninteger\n%i\n" % (BASE, key, key)
		DATA["%s.2.%i" % (BASE, key)] = "%s.2.%i\nstring\n%s\n" % (BASE, key, inst_name)

	#print DATA
	#sys.exit(1)

	for key in QUEUES:
		DATA["%s.3.%i" % (BASE, key)] = "%s.3.%i\ninteger\n%i\n" % (BASE, key, key)
		DATA["%s.4.%i" % (BASE, key)] = "%s.4.%i\nstring\n%s\n" % (BASE, key, QUEUES[key])

	#print DATA
	#sys.exit(1)

	for inst_key in INSTANCES_Q_DIRS:
		for queues_key in QUEUES:
			DATA["%s.5.%i.%i" % (BASE, inst_key, queues_key)] = {"instance" : INSTANCES_Q_DIRS[inst_key], "queue": QUEUES[queues_key]}
	for queues_key in QUEUES:
		for inst_key in INSTANCES_Q_DIRS:
			DATA["%s.6.%i.%i" % (BASE, queues_key, inst_key)] = {"instance" : INSTANCES_Q_DIRS[inst_key], "queue": QUEUES[queues_key]}
	
	
	#for queue in QUEUES:
	#	#print "%s: \n\t" % queue
	#	DATA["%s.1.%i" % (BASE,q_num)] = "%s.1.%s\ninteger\n%s\n" % (BASE, q_num, q_num)
	#	#print DATA["%s.1.1" % BASE]
	#	DATA["%s.2.%i" % (BASE,q_num)] = "%s.2.%s\nstring\n%s\n" % (BASE, q_num, queue)
	#	for instance in INSTANCES_Q_DIRS:
	#		inst_name = os.path.basename(instance)
	#		DATA["%s.3.%i.1.%i" % (BASE,q_num,inst_num)] = "%s.3.%i.1.%i\ninteger\n%i" % (BASE,q_num,inst_num,inst_num)
	#		DATA["%s.3.%i.2.%i" % (BASE,q_num,inst_num)] = "%s.3.%i.2.%i\nstring\n%s\n" % (BASE,q_num,inst_num,inst_name)
	#		#COUNT = os.popen("find %s/%s/ -type f | wc -l" % (instance,queue) ).read()
	#		#print "%s:%s \n\t" % (instance,COUNT)
	#		#DATA["%s.3.%i.3.%i" % (BASE,q_num,inst_num)] = "%s.3.%i.3.%i\ninteger\n%i\n" % (BASE,q_num,inst_num,int(COUNT))
	#		DATA["%s.3.%i.3.%i" % (BASE,q_num,inst_num)] = {"instance" : instance, "queue": queue}
	#		inst_num = inst_num+1
	#	#DATA["%s.3.%i.3.%i" % (BASE,q_num,inst_num-1)]["next"] = "%s.1.%i" % (BASE,q_num+1)
	#	#print DATA["%s.1.1" % BASE]
	#	inst_num = 1
	#	q_num = q_num + 1
	#	#print "\n"
	
	#print DATA["%s.1.1" % BASE]

	#sorted_keys=sorted(DATA, key=DATA.get)
	sorted_keys=DATA.keys()
	sort_nicely(sorted_keys)
	#sorted_keys.sort()
	#for k in sorted_keys:
	#	print "%i:%s" % (sorted_keys.index(k), k)
	#sys.exit(0)
	#print DATA["%s.1.1" % BASE]

	if REQ_T == '-g':
		#print DATA[REQ]
		#print DATA["%s.1.1" % BASE]

		print get_data(str(REQ))
	elif REQ_T == '-n':
		if REQ == BASE: 
			#print DATA["%s.1.1" % BASE]
			#print get_data("%s.1.1" % BASE)
			print get_data(sorted_keys[0])
		elif DATA.has_key(REQ) is False:
			pos = [i for i,x in enumerate(sorted_keys) if x.find(REQ) >= 0][0]
			#print "@%i" % pos
			#print "#%s" % sorted_keys[pos]
			#print DATA[sorted_keys[pos]]
			#print "$ %i > %i" % (len(sorted_keys[pos]), len(REQ))
			if len(sorted_keys[pos]) > len(REQ):
				next = sorted_keys[pos]
			else:
				next = sorted_keys[pos+1]
			#next = sorted_keys[sorted_keys.index(REQ)+1]
			print get_data(next)
			#if DATA.has_key(REQ+".1") is True:
			#	#print DATA["%s.1" % REQ]
			#	print get_data("%s.1" % REQ)
			#elif DATA.has_key(REQ+".1.1") is True:
			#	#print DATA["%s.1.1" % REQ]
			#	print get_data("%s.1.1" % REQ)
			#elif DATA.has_key(REQ+".1.1.1") is True:
			#	#print DATA["%s.1.1.1" % REQ]
			#	print get_data("%s.1.1.1" % REQ)
		elif DATA.has_key(REQ) is True:
			next = sorted_keys[sorted_keys.index(REQ)+1]
			#print DATA[next]
			print get_data(next)
	#		if REQ[-3] == next[-3]:
	#			#print DATA[sorted_keys[sorted_keys.index(REQ)+1]]
	#			print DATA[next]
	#		elif len(REQ) 
		else:
			#print DATA["%s.1.1" % BASE]
			print get_data("%s.1.1" % BASE)
	else:
		print """Read help please"""


if __name__ == '__main__':
	main()
