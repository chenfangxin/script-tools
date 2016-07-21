#!/usr/bin/python

import os
import json
import ethtool
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring 

def presist_vmname(vmname):
	node = Element('name')
	node.text = vmname
	return node

def presist_cpuset(cpuset):
	count = len(cpuset)
	cputune = Element('cputune')
	idx = 0
	while idx<count:
		vcpupin = Element('vcpupin')	
		vcpupin.set('vcpu', str(idx))
		vcpupin.set('cpuset', str(cpuset[count-idx-1]))
		cputune.append(vcpupin)
		idx = idx + 1
	return cputune

def get_host_pci_addr(ifname):
	businfo = ethtool.get_businfo(ifname)	
	l = businfo.split(':')
	s = l[2].split('.')
	del l[2]
	l.extend(s)	
	l = map(lambda x:'0x'+x, l)
	addr = {}
	addr['domain'] = l[0]
	addr['bus'] = l[1]
	addr['slot'] = l[2]
	addr['function'] = l[3]
	return addr

def get_target_pci_addr(ifname):
	ifname = ifname[5:]
	addr = {}
	addr['domain'] = '0x0000'
	addr['bus'] = '0x2'
	addr['slot'] = '0x' + str(int(ifname)+1)
	addr['function'] = '0x00'
	return addr

def presist_ifset(item):
	host_addr = get_host_pci_addr(item['ifname'])	
	source = Element('source')
	sub_source = Element('address')
	sub_source.set('type', 'pci')
	sub_source.set('domain', host_addr['domain'])
	sub_source.set('bus', host_addr['bus'])
	sub_source.set('slot', host_addr['slot'])
	sub_source.set('function', host_addr['function'])
	source.append(sub_source)
	
	target_addr = get_target_pci_addr(item['ifname'])
	address = Element('addrss')
	address.set('type', 'pci')
	address.set('domain', target_addr['domain'])
	address.set('bus', target_addr['bus'])
	address.set('slot', target_addr['slot'])
	address.set('function', target_addr['function'])

	if item['vlanid']:
		vlan = Element('vlan')
		subnode = Element('tag')
		subnode.set('id', item['vlanid'])
		vlan.append(subnode)

		child = Element('interface')
		child.set('type', 'hostdev')
		child.append(source)
		child.append(vlan)
		child.append(address)
	else:
		child = Element('hostdev')	
		child.set('mode', 'subsystem')
		child.set('type', 'pci')
		child.set('managed', 'yes')
		child.append(source)
		child.append(address)
	return child
	
def create_xml(cfg):
	elem = Element('domain')			
	elem.set('type', 'kvm')
	
	child = presist_vmname(cfg['vmname'])
	elem.append(child)		

	child = Element('vcpu')
	child.text = str(len(cfg['cpuset']))
	elem.append(child)

	child = presist_cpuset(cfg['cpuset'])
	elem.append(child)
	
	child = Element('memory')
	child.set('unit', 'GiB')
	child.text = str(cfg['memsize'])
	elem.append(child)

	child = Element('memoryBacking')
	subchild = Element('hugepages')
	child.append(subchild)
	elem.append(child)

	child = Element('os')
	subchild = Element('type')
	subchild.set('arch', 'x86_64')
	subchild.text = 'hvm'
	child.append(subchild)
	subchild = Element('boot')
	subchild.set('dev', 'hd')
	child.append(subchild)
	elem.append(child)

	child = Element('features')
	subchild = Element('acpi')
	child.append(subchild)
	elem.append(child)

	child = Element('on_poweroff')
	child.text = 'destroy'
	elem.append(child)

	child = Element('on_reboot')
	child.text = 'restart'
	elem.append(child)

	child = Element('clock')
	child.set('sync', 'localtime')
	elem.append(child)

	child = Element('devices')
	subchild = Element('emulator')
	subchild.text = '/usr/bin/qemu-kvm'
	child.append(subchild)

	subchild = Element('serial')
	subchild.set('type', 'pty')
	sub_subchild = Element('target')
	sub_subchild.set('port', '0')
	subchild.append(sub_subchild)
	child.append(subchild)

	subchild = Element('console')
	subchild.set('type', 'pty')
	sub_subchild = Element('target')
	sub_subchild.set('type', 'serial')
	sub_subchild.set('port', '0')
	subchild.append(sub_subchild)
	child.append(subchild)

	subchild = Element('disk')
	subchild.set('type', 'file')
	subchild.set('device', 'disk')
	sub_subchild = Element('driver')
	sub_subchild.set('name', 'qemu')
	sub_subchild.set('type', 'raw')
	sub_subchild.set('cache', 'none')
	subchild.append(sub_subchild)
	sub_subchild = Element('source')
	filepath = os.path.join('/mnt1/virtual_machine', cfg['vmname'], cfg['vmname']+'.vcf')
	sub_subchild.set('file', filepath)
	subchild.append(sub_subchild)
	sub_subchild = Element('target')
	sub_subchild.set('dev', 'hda')
	sub_subchild.set('bus', 'ide')
	subchild.append(sub_subchild)
	child.append(subchild)

	subchild = Element('interface')
	subchild.set('type', 'bridge')
	sub_subchild = Element('mac')
	sub_subchild.set('address', cfg['mgt_mac'])
	subchild.append(sub_subchild)
	sub_subchild = Element('source')
	sub_subchild.set('bridge', 'br0')
	subchild.append(sub_subchild)
	sub_subchild = Element('model')
	sub_subchild.set('type', 'virtio')
	subchild.append(sub_subchild)
	child.append(subchild)

	for item in cfg['ifset']:
		subchild = presist_ifset(item)
		child.append(subchild)

	elem.append(child)

	return elem

def indent(elem, level=0):
	i = '\n' + level * '  '

	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + '  '
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for subelem in elem:
			indent(subelem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

if __name__=='__main__':
	vmconfig = './vmconfig.json'
	cfg = {}

	with open(vmconfig, 'rt') as f:
		cfg = json.load(f)	

	if cfg:
		e = create_xml(cfg)
		indent(e)
	else:
		print "Failt to load vmconfig.json file"
		sys.exit(0)

	xmlfile = './' + cfg['vmname'] + '.xml'
	with open(xmlfile, 'wt') as f:
		f.write(tostring(e))
