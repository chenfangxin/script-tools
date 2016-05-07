# 准备LVM卷
用如下命令：
```
    apt-get install lvm2
    pvcreate /dev/sda4      # 在分区上建立PV
    vgcreate vg0 /dev/sda4  # 创建名为vg0的卷组
    lvcreate -n centos7 -L 20G vg0  # 创建名为centos7的卷
```

# 安装XEN
用如下命令：
```
    apt-get install xen-linux-system
```

# 准备网络
本例中，使用Linux Bridge连接虚拟机和物理接口
用如下命令安装Bridge工具：
```
    apt-get install bridge-utils
```
在```/etc/network/interfaces```文件中，设置系统网络：
```
auto eth0
iface eth0 inet manual

auto xenbr0
iface xenbr0 inet static
    bridge_ports eth0
    address 192.168.1.148
    netmask 255.255.255.0
    gateway 192.168.1.1
```

# 创建虚拟机的配置文件
虚拟机的配置文件，名为centos7.cfg，内容如下：
```
kernel  = "/usr/lib/xen-4.4/boot/hvmloader"
builder = "hvm"
memory  = 4096
vcpus   = 4
name    = "centos7"
vif     = ['type=vif,bridge=xenbr0']
# disk    = ['/home/ratel/centos7.img,qcow2,xvda,rw']
disk    = ['phy:/dev/vg0/centos7,hda,w','file:/root/Downloads/centos7.iso,hdc:cdrom,r']
acpi    = 1
device_model_version = 'qemu-xen'
boot    = "a"
sdl     = 0
serial  = 'pty'
vnc     = 1
vncdisplay  = 1
vnclisten   = ""
vncpasswd   = ""
```
虚拟机使用的硬盘镜像，可以是raw格式的(用dd创建)，也可以是qcow2格式的(用qemu-img创建)，还可以是LVM的一个卷,这三者在disk域中区分。

# 创建虚拟机
用如下命令：
```
    xl create centos7.cfg
    xvnc4viewer 192.168.1.148:5901  # port由vncdisplay决定
```
