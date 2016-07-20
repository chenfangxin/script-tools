#!/usr/bin/python

import os
import json
import ethtool
from lxml import etree

def presist_vmname(root, vmname):
	name = etree.SubElement(root, 'name')
	name.text = cfg['vmname']

def presist_cpuset(root, cpuset):
	count = len(cpuset)
	vcpu = etree.SubElement(root, 'vcpu')
	vcpu.text = str(count)

	cputune = etree.SubElement(root, 'cputune')
	idx=0
	while idx<count:
		vcpupin = etree.SubElement(cputune, 'vcpupin')		
		vcpupin.attrib['vcpu'] = str(idx)
		vcpupin.attrib['cpuset'] = str(cpuset[count-idx-1])
		idx = idx + 1

def presist_memsize(root, memsize):
	memory = etree.SubElement(root, 'memory')
	memory.attrib['unit'] = 'GiB'
	memory.text = str(memsize)
	memoryBacking = etree.SubElement(root, 'memoryBacking')
	etree.SubElement(memoryBacking, 'hugepages')

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

def presist_ifset(root, ifset):
	for item in ifset:
		host_addr = get_host_pci_addr(item['ifname'])
		source = etree.Element('source')			
		sub_source = etree.SubElement(source, 'address')
		sub_source.attrib['type'] = 'pci'
		sub_source.attrib['domain'] = host_addr['domain']
		sub_source.attrib['bus'] = host_addr['bus']
		sub_source.attrib['slot'] = host_addr['slot']
		sub_source.attrib['function'] = host_addr['function']

		target_addr = get_target_pci_addr(item['ifname'])
		address = etree.Element('address')
		address.attrib['type'] = 'pci'
		address.attrib['domain'] = target_addr['domain']
		address.attrib['bus'] = target_addr['bus']
		address.attrib['slot'] = target_addr['slot']
		address.attrib['function'] = target_addr['function']
		
		if item['vlanid']:
			vlan = etree.Element('vlan')
			subnode = etree.SubElement(vlan, 'tag')
			subnode.attrib['id'] = item['vlanid']

			child = etree.SubElement(root, 'interface')
			child.attrib['type'] = 'hostdev'
			child.append(source)
			child.append(address)
			child.append(vlan)
		else:
			child = etree.SubElement(root, 'hostdev')
			child.attrib['mode'] = 'subsystem'
			child.attrib['type'] = 'pci'
			child.attrib['managed'] = 'yes'
			child.append(source)
			child.append(address)
	
def create_xml(cfg):
	root = etree.Element('domain')
	root.attrib['type'] = 'kvm'

	presist_vmname(root, cfg['vmname'])
	presist_cpuset(root, cfg['cpuset'])
	presist_memsize(root, cfg['memsize'])

	os = etree.SubElement(root, 'os')
	subnode = etree.SubElement(os, 'type')
	subnode.attrib['arch'] = 'x86_64'
	subnode.text = 'hvm'

	boot = etree.SubElement(os, 'boot')
	boot.attrib['dev'] = 'hd'

	features = etree.SubElement(root, 'features')
	etree.SubElement(features, 'acpi')

	on_poweroff = etree.SubElement(root, 'on_poweroff')
	on_poweroff.text = 'destroy'

	on_reboot = etree.SubElement(root, 'on_reboot')
	on_reboot.text = 'restart'

	clock = etree.SubElement(root, 'clock')
	clock.attrib['sync'] = 'localtime'

	devices = etree.SubElement(root, 'devices')
	subnode = etree.SubElement(devices, 'emulator')
	subnode.text = '/usr/bin/qemu-kvm'

	subnode = etree.SubElement(devices, 'serial')
	subnode.attrib['type'] = 'pty'
	sub_subnode = etree.SubElement(subnode, 'target')
	sub_subnode.attrib['port'] = '0'

	subnode = etree.SubElement(devices, 'console')
	subnode.attrib['type'] = 'pty'
	sub_subnode = etree.SubElement(subnode, 'target')
	sub_subnode.attrib['type'] = '0'
	sub_subnode.attrib['port'] = '0'
	
	subnode = etree.SubElement(devices, 'disk')
	subnode.attrib['type'] = 'file'
	subnode.attrib['device'] = 'disk'
	sub_subnode = etree.SubElement(subnode, 'driver')
	sub_subnode.attrib['name'] = 'qemu'
	sub_subnode.attrib['type'] = 'raw'
	sub_subnode.attrib['cache'] = 'none'

	sub_subnode = etree.SubElement(subnode, 'source')
	filepath = '/mnt1/virtual_machine' + '/' + cfg['vmname'] + '/' + cfg['vmname']+'.vcf'
	sub_subnode.attrib['file'] = filepath
	
	subnode = etree.SubElement(devices, 'interface')
	sub_subnode = etree.SubElement(subnode, 'mac')
	sub_subnode.attrib['address'] = cfg['mgt_mac']
	sub_subnode = etree.SubElement(subnode, 'source')
	sub_subnode.attrib['bridge'] = 'br0'
	sub_subnode = etree.SubElement(subnode, 'model')
	sub_subnode.attrib['type'] = 'virtio'

	presist_ifset(devices, cfg['ifset'])

	return root

if __name__=='__main__':
	vmconfig = './vmconfig.json'
	cfg = {}
	with open(vmconfig) as f:
		cfg = json.load(f)
	if cfg:
		a = create_xml(cfg)
 		print etree.tostring(a, pretty_print=True)
