#!/usr/bin/python
import os
import sys
import subprocess
import json

def get_vlb_mgtip(idx):
    mgtip = "10.1.0." + str(idx)
    return mgtip

def get_vlb_cpu(idx):
    cpuidx = (idx-1) / 8
    return cpuidx

def create_ifinfo(idx):
    ifinfo = {}
    ifname = "xge1_" + str((idx-1) / 8)
    if_tag = 100 + idx
    ifinfo["ifname"] = ifname
    ifinfo["vlanid"] = if_tag
    return ifinfo

#create vmconfig.json 
def create_vmconfig(idx):
    vmconfig = {}
    vmname = "vlb" + str(idx)
    vmconfig["vmname"] = vmname
    vmconfig["cpuset"] = []
    cpuidx = get_vlb_cpu(idx)
    vmconfig["cpuset"].append(0)
    vmconfig["cpuset"].append(cpuidx)
    vmconfig["memsize"] = 750
    vmconfig["disksize"] = 2
    mgtip = get_vlb_mgtip(idx)
    vmconfig["mgtip"] = mgtip
    vmconfig["ifset"] = []
    ifinfo = create_ifinfo(idx)
    vmconfig["ifset"].append(ifinfo)
    # encodejson = json.dumps(vmconfig)
    # print encodejson
    filename = vmname + "/vmconfig.json"
    with open(filename, 'w') as file:
        file.write(json.dumps(vmconfig))

def create_vm_img(vmname):
    os.system("cp templete-new.vcf %s/%s.vcf" % (vmname, vmname))
    vcf_img = "/mnt1/virutal_machine/" + vmname + "/" + vmname + ".vcf"

    devname = subprocess.Popen(["kpartx", "-avs", vcf_img], stdout=subprocess.PIPE).communicate()[0].split()[2]
    print devname

    os.system("mount /dev/mapper/%s %s/vcf" % (devname, vmname))

    os.system("cp kernel.img %s/vcf/boot/" % vmname)
    os.system("cp rootfs.img %s/vcf/boot/" % vmname)
    os.system("cp license %s/vcf/boot/" % vmname)
    os.system("cp utmcfg.con %s/vcf/boot/" % vmname)

    os.system("sync");

    os.system("umount %s/vcf" % vmname)
    os.system("kpartx -d /mnt1/virutal_machine/%s/%s.vcf" % (vmname, vmname))

if __name__ == "__main__":
    for idx in range(1, 3):
        vmname="vlb"+str(idx)
        os.system("mkdir -p %s/vcf" % vmname)
        ifinfo = create_ifinfo(idx)
        create_vmconfig(idx)

        # create_vm_img(vmname)

