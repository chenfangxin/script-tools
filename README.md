# dpdk-test
dpdk的应用实验

#DPDK+OVS
use libvirt-1.2.21;
install libpciaccess-devel, libxml2-devel, libnl3-devel, device-mapper-devel, numactl-devel, gtk3-spice-devel,gtk-vnc2-devel,...

./autogen.sh --system
make
make install

<interface type='vhostuser'>
	<mac address='XX:XX:...'/>
	<source type='unix' path='/var/run/openvswitch/vhost-user-0' mode='client'/>
	<model type='virtio'/>
</interface>
