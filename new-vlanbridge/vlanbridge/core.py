#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
vlanbridge.core

This module privides func to create ,del ,vlanbridge
"""

import os
import sys
sys.path.append("..")
from log import logfile
import glob
import commands
import time
import json
import logging
import pdb
IF_CFG_FILE_PATH='/etc/sysconfig/network-scripts/'
RC_LOCAL_PATH='/etc/rc.local'
#get nic by path
def filternics(path):
    nics=[b.split('/')[-2] for b in glob.glob(path)]
    return [b.split('/')[-2] for b in glob.glob(path)]

#get nics exclude wireless
def init_nics():
    WLAN_PATH= '/sys/class/net/*/wireless'
    NIC_PATH='/sys/class/net/*/device'
    global nic_list
    nic_list = list( set(filternics(NIC_PATH)) -set(filternics(WLAN_PATH)))
#new a file in /etc/sysconfig/network-scripts
def newfile(lines,filepath):
    try:
        with open(filepath,"w+") as fw:
            for l in lines:
                fw.write(l)
    except Exception as e:
        logging.info(e)

#new a file such as ifcfg-em1.4088
def define_ifcfgfile(nicname,vlanId):
    ifname=str.format('%s.%d'%(nicname, vlanId))
    brname=str.format('br1.%d'%vlanId)
    ifconfgName = str.format('ifcfg-%s.%d' %(nicname, vlanId))
    ifconfigPath = IF_CFG_FILE_PATH + ifconfgName
    L =[]
    L.append('DEVICE=' + ifname +'\n')
    L.append('ONBOOT=yes"\n')
    L.append('BRIDGE=' + brname +'\n')
    L.append('TYPE=Ethernet"\n')
    L.append('BOOTPROTO=static"\n')
    L.append('NM_CONTROLLED=no"\n')
    newfile(L,ifconfigPath)
    logging.info("create iface %s ok" %ifconfigPath)


#new a file such as ifcfg-br1.4088
def define_brcfgfile(vlanId):
    brname=str.format('br1.%d'%vlanId)
    brconfgName =str.format('ifcfg-br1.%d' %vlanId)
    brconfigPath = IF_CFG_FILE_PATH + brconfgName
    L =[]
    L.append('DEVICE=' + brname +'\n')
    L.append('ONBOOT=yes"\n')
    L.append('TYPE=Bridge"\n')
    L.append('BOOTPROTO=static"\n')
    L.append('NM_CONTROLLED=no"\n')
    L.append('NAME=' + brname+'\n')
    newfile(L,brconfigPath)
    logging.info("create Br %s ok" %brconfigPath)


def defineEnv():
    os.system('chmod +x %s'%RC_LOCAL_PATH)
    lines=None
    is8021q = False
    with open(RC_LOCAL_PATH,"r") as fr:
        lines = fr.readlines()
        for l in lines:
            if '8021q' in l:
                is8021q = True
        if is8021q == False:
            cmdline=str.format('sed -i "1a modprobe 8021q" %s' %RC_LOCAL_PATH) 
	    call_os_run(cmdline)

def call_os_run(commandline):
    try:
        os.system('%s'%commandline)
        logging.info('%s'%commandline)
    except Exception as e:
        logging.info('call_os_run %s:%s'%(commandline,e))

def vconf(nicname, vlanId):
    ifacename=str.format('%s.%d'%(nicname,vlanId))
    lines = None
    try:
        with open(RC_LOCAL_PATH,'r') as fr:
            lines = fr.readlines()
    except Exception as e:
        logging.info(e)
    #write vconfig add %nicname %vlanid to rc.local
    isExist = False
    for l in lines:
        if nicname in l and vlanId in l:
            isExist = True
    if isExist == False:
        cmdline = str.format('vconfig add %s %d' %(nicname,vlanId))
        call_os_run(cmdline)
    cmdlines = [str.format('ifconfig %s up'%ifacename),
                str.format('brctl addbr br1.%d'%vlanId),
                str.format('brctl addif br1.%d %s' %(vlanId,ifacename)),
                str.format('ifconfig br1.%d up' %vlanId)]
    results=map(call_os_run,cmdlines)

def read_nicname():
    nic_name = None
    while True:
        print("=======input Nic name as:em1")
        nic_name = raw_input('name:')
        if nic_name in nic_list:
            break
        else:
            print('%s not exist,please input again or Ctrl+D to quit!' % nic_name)
    logging.info('input nic name: %s' %nic_name)
    return nic_name

def read_vlanId():
    vlanId = None
    while True:
        print("=======input vlan Id as: 4088")
        vlanId = int(raw_input('vlanId:'))
        if not isinstance(vlanId,int):
            print('%d not available,please input again or Ctrl+D to quit!' % vlanId)
        if 0<vlanId<4096:
            break
        else:
            print('%d not available,please input again or Ctrl+D to quit!' % vlanId)
    logging.info('input nic name: %d' %vlanId)
    return vlanId

def create_Bridge():
    
    #pdb.set_trace()
    nicname = read_nicname()
    vlanId = read_vlanId()
    define_ifcfgfile(nicname, vlanId)
    define_brcfgfile(vlanId)
    vconf(nicname,vlanId)
    print('Finished create_Bridge !!!\n')
def get_ifaces():
    # getoutput :'br0\nbr1.4088\nem1\nem2\nem2.4088\nlo\nvirbr0'
    return (commands.getoutput("ifconfig | grep 'flag' | awk -F ':' '{print $1}'")).split('\n')

def read_ifacename():
    iface_name = None
    while True:
        print('=======input face name as:em1.4088')
        iface_name = raw_input('name:')
        if iface_name in ifaces and 'br1' not in iface_name:
            break
        else:
            print('%s not exist,please input again or Ctrl+D to quit!' % iface_name)
    logging.info('input iface_name: %s' %iface_name)
    return iface_name

def read_brfacename():
    brface_name = None
    while True:
        print("=======input brface name as:br1.4088")
        brface_name = raw_input('name:')
        if brface_name in ifaces and 'br' in brface_name:
            break
        else:
            print('%s not exist,please input again or Ctrl+D to quit!' % brface_name)
    logging.info('input brface_name: %s' % brface_name)
    return brface_name

def remove_faces(iface_to_move,brface_to_move):
    ifcfgfile = str.format('ifcfg-%s' %iface_to_move)
    ifbrcfgfile = str.format('ifcfg-%s' %brface_to_move)
    ifcfgfile_path = IF_CFG_FILE_PATH + ifcfgfile
    brcfgfile_path = IF_CFG_FILE_PATH + ifbrcfgfile

    cmdlines=[str.format('ifconfig %s down' %iface_to_move),
              str.format('ifconfig %s down' %brface_to_move),
              str.format('brctl delif %s %s' %(brface_to_move,iface_to_move)),
              str.format('brctl delbr %s' %brface_to_move),
              str.format('vconfig rem %s' %iface_to_move),
              str.format('rm -f %s' %ifcfgfile_path),
              str.format('rm -f %s' %brcfgfile_path)]
    results = map(call_os_run,cmdlines)
    print('Finnished remove_faces !!!!\n')

def remove_Bridge():
    global ifaces
    ifaces=get_ifaces()
    print("==========ifaces===============")
    print(ifaces)
    print("===============================")
    iface_to_move = read_ifacename()
    brface_to_move= read_brfacename()
    remove_faces(iface_to_move,brface_to_move)

def show_help():
    help_text = """

       this is a description about how to create a vlan-bridge
       To create a vlan-bridge
       first choose a nic which is connect to a Trunk-port by 1)list nics
       then give a VlanId as: 4088
       To remove a vlan-bridge,
       """
    print(help_text)
def show_options():
    userage_text="""
======================================
 1) list nics        2)create iface
 3) remove iface     4) help
 5) exit
======================================
    """
    print(userage_text)
def show_loop():
    while True:
        show_options()
        case = int(raw_input("Input Your option:"))
        if not isinstance(case,int):
            print('%d not available,please input again or Ctrl+D to quit!' % case)
            continue
        if case == 1:
           print('================nics===================')
           print(nic_list)           
        if case == 2:
            create_Bridge()
        if case == 3:
            remove_Bridge()
        if case == 4:
            show_help()
        if case == 5:
            break
        else:
            pass
    return

def main():
     
    logfile("./newvlanbridge.log")
    try:
        init_nics()
        defineEnv()
        show_loop()
    except BaseException as e:
        logging.info(e)
    logging.info("finnished!!")
    return
if __name__ == '__main__':
    main()
