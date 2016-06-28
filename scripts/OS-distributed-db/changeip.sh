#!/bin/bash

# gets the ips from the file given in argument, which is supposed to have received
# the result for "ifconfig eth0" from both VMs.
ipfile="$1"
grep "inet addr:" $ipfile | cut -d: -f2 | awk '{ print $1}' > ips.txt
ipmysql=$(head -1 ips.txt)
ipredis=$(tail -1 ips.txt)
echo $ipmysql
echo $ipredis

# stores them in the discovery-vagrant scripts for deployment
cmd="sed -i 's\/\^redis_cluster_enabled: False\$\/\&\\\nnodes=${ipredis}\/' rome.conf"
  # add a "MYSQL_HOST=<IpAddressForMySqlDB>" before EOM in file 05_devstack.sh
sed -i "s/^EOM$/MYSQL_HOST=${ipmysql}\n&/" discovery-vagrant/05_devstack.sh
  # add a "sed -i s/^redis_cluster_enabled: False$/&\nnodes=<IpAdressForRedisDB>/ rome.conf"
  # line to 02_rome.sh which will enable to put the ip adress in rome.conf during the
  # discovery-vagrant deployment.
sed -i "s/^pushd rome\s*$/&\n${cmd}/" discovery-vagrant/02_rome.sh
