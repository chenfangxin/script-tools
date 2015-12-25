# script-tools

##编译DPDK+OVS

使用qemu-2.4.1, libvirt-1.2.21, DPDK-2.1.0+, OVS-2.4.0+;

编译qemu前，需要安装如下开发库：  
libpciaccess-devel, libxml2-devel, libnl3-devel, device-mapper-devel, numactl-devel, gtk3-spice-devel,gtk-vnc2-devel,...

dpdkvhostuser接口在VM的xml中的描述：  
```
<interface type='vhostuser'>
	<mac address='XX:XX:...'/>
	<source type='unix' path='/var/run/openvswitch/vhost-user-0' mode='client'/>
	<model type='virtio'/>
</interface>
```
