#!/bin/bash

# This script enables devstack to use remotes mysql and redis databases.
# It takes a text file as argument, which is supposed to have received
# the result of "ifconfig eth0" from both VMs.

# gets the ips from the file
ip="$1"
 

# stores them in the discovery-vagrant scripts for deployment
cmd="sed -i 's\/\^redis_cluster_enabled: False\$\/\&\\\nnodes=${ip}\/' rome.conf"
  # add a "MYSQL_HOST=<IpAddressForMySqlDB>" before EOM in file 05_devstack.sh
sed -i "s/^EOM$/MYSQL_HOST=${ip}\nMYSQL_USER=stack\nMYSQL_PASSWORD=devstack\n&/" discovery-vagrant/05_devstack.sh
  # add a "sed -i s/^redis_cluster_enabled: False$/&\nnodes=<IpAdressForRedisDB>/ rome.conf"
  # line to 02_rome.sh which will enable to put the ip adress in rome.conf during the
  # discovery-vagrant deployment.
sed -i "s/^pushd rome\s*$/&\n${cmd}/" discovery-vagrant/02_rome.sh
