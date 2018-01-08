#!/bin/bash
# This script is for create subinterface and add to bridge
# First select a interface connect to a Trunk Port ,for example eth1
# touch /etc/sysconfig/ifconfig-eth1.4088
# touch /etc/sysconfig/ifconfig-br1.4088
# edit ifconfig-eth1.4088 and ifconfig-br1.4088
# add vlanid 4088 to eth1
# ifconfig eth1.4088  up
# brctl addbr br1.4088
# brctl addif br1.4088 eth1.4088
#
modprobe 8021q
IF_PATH='/etc/sysconfig/network-scripts/'
function createvlanif()
{
	nicname=$1
	vlanid=$2
	echo "nicname $nicname"
	echo "vlanid $vlanid"
	tempcmd=`sed 's/ONBOOT=no/ONBOOT=yes/g' /${IF_PATH}ifcfg-${nicname}`
	echo $tempcmd >null
	if cd $IF_PATH;
	then
		newifName=${nicname}.${vlanid}     
		newbrName=br1.${vlanid}

		newifcfgName=ifcfg-$newifName
		newbrcfgName=ifcfg-$newbrName

		if touch ${newifcfgName};
		then 
			echo $null>${newifcfgName}
			echo "DEVICE=${newifName}" >> ${newifcfgName}
			echo "ONBOOT=yes">>${newifcfgName}
			echo "BRIDGE=${newbrName}" >> ${newifcfgName}
			echo "TYPE=Ethernet" >> ${newifcfgName}  
			echo "BOOTPROTO=static" >> ${newifcfgName}
			echo "NM_CONTROLLED=no" >> ${newifcfgName}
		else
			echo "create file ${newifcfgName} fails" 1>&2
			exit 1;	
		fi
	
		if touch ${newbrcfgName};
		then
	
			echo $null>${newbrcfgName}
			echo "DEVICE=${newbrName}" >> ${newbrcfgName} 
			echo "BOOTPROTO=static" >> ${newbrcfgName} 
			echo "TYPE=Bridge" >> ${newbrcfgName}
			echo "ONBOOT=yes" >> ${newbrcfgName}
			echo "NAME=${newbrName}" >> ${newbrcfgName} 
			echo "NM_CONTROLLED=no" >> ${newbrcfgName} 
		else
			echo "create file ${newbrcfgName} fails" 1>&2
			exit 1;
		fi
		##add br ,then add if to br you create
		## up the br and if
		### enable rc.local auto excute when boot
		chmod +x /etc/rc.local
		
		##enable 8021q,by write str to second line
		modstr="modprobe 8021q"
		modgrep=`cat /etc/rc.local |grep "$modstr"`
		res=echo $modgrep 
		if 
			cat /etc/rc.local |grep "$modstr"
		then 
			sed  -i "1a $modstr" /etc/rc.local	
		fi
		
		##write vconfig add xx xx to rc.local
		
		vcfgstr="vconfig add $nicname $vlanid"
		if
			cat /proc/net/vlan/config | grep "${nicname}.${vlanid}"
		then
			vconfig rem $newifName
		fi
		echo `$vcfgstr`
		cat /etc/rc.local | grep "$vcfgstr"
		if 
			cat /etc/rc.local | grep "$vcfgstr"
		then
			echo "already exist"
		else
			echo "$vcfgstr" >>/etc/rc.local
		fi
		
		
		ifconfig $newifName up
		brctl addbr $newbrName 
		brctl addif $newbrName $newifName
		ifconfig $newbrName up
	else	
		echo "cannot change to /etc/sysconfig/network-scripts/" 1 >$2
		exit 1;
	fi

}
function delinterface()
{
	vlanif=$1
	vlanbr=$2
	ifcfgfile=ifcfg-$vlanif
	brcfgfile=ifconfig-$vlanbr
	downif=`ifconfig $vlanif down`
	downbr=`ifconfig $vlanbr down`
	delif=`brctl delif $vlanbr $vlanif`
	delbr=`brctl delbr $vlanbr`
	delvlan=`vconfig rem $vlanif`
	#delvconfig=`sed -i "/$vlan" /etc/rc.local`
	#to do
	if echo $downif;
	then
		echo "ifconfig down $vlanif success"
	else
		echo "ifconfig down $vlanif  fails"
	fi
	
	if echo $downbr;
	then
		echo "ifconfig down $vlanbr success"
	else
		echo "ifconfig down $vlanbr fails"	
	fi
	if echo $delif;
	then 
		echo "delete $vlanif from $vlanbr success"
	else	
		echo "delete $vlanif from $vlanbr fails"
	fi	
	if echo $delbr;
	then
		echo "delete $vlanbr success"
	else
		echo "delete $vlanbr fails"
	fi
	if echo $delvlan;
	then 
		echo "delete $vlanbr success"
	else 
		echo "delete $vlanbr fails"
	fi
	rm -rf /etc/sysconfig/network-scripts/ifcfgfile
	rm -rf /etc/sysconfig/network-scripts/brcfgfile
}
comand_listiface="ifconfig | grep  'flags' | awk -F ':' '{print $1}"
ch_createif='Create Interface'
ch_removeif='Remove Interface'
ch_listnic='List Nics'
ch_exit='exit' 
echo "before slect"
select ch in "$ch_createif" "$ch_removeif" "$ch_listnic" "$ch_exit"
do 
	case $ch in 
	"${ch_createif}")
		echo "Choose a NIC to create interface"
		echo "======input Nic Name======="
		read nic
		echo "nic:$nic"
		echo "======input Vlan ID as:4088======="
		read id
		echo "id: $id"
                ifconfig $nic up
		createvlanif $nic $id
		;;
	"${ch_removeif}")
		echo "Choosen a Interface to Remove"
		#listitfaces
        	ifconfig | grep  'flags' | awk -F ':' '{print $1}'
		echo "======input Interface======="
		read iface
		echo "======input br======="
		read br
		delinterface $iface $br
		;;
	"${ch_listnic}")
		echo "==============Nic lists========="
        	ifconfig | grep  'flags' | awk -F ':' '{print $1}'
		;;
	"${ch_exit}")
		echo "exit"
		exit 0
		;;
	*)
		echo "Default"
		;;
	esac
done
;
