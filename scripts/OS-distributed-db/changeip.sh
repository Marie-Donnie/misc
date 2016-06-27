#!/bin/bash


ipfile="$1"
grep "inet addr:" $ipfile | cut -d: -f2 | awk '{ print $1}' > ips.txt
ipmysql=$(head -1 ips.txt)
ipredis=$(tail -1 ips.txt)
echo $ipmysql
echo $ipredis
           
cmd="sed -i 's\/\^redis_cluster_enabled: False\$\/\&\\\nnodes=${ipredis}\/' rome.conf"

sed -i "s/^EOM$/MYSQL_HOST=${ipmysql}\n&/" discovery-vagrant/05_devstack.sh
sed -i "s/^pushd rome\s*$/&\n${cmd}/" discovery-vagrant/02_rome.sh
