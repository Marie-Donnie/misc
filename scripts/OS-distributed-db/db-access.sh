#!/bin/bash

# This script enables the remote connection of stack user to mysql database

# grants access to stack user
mysql -u root -e "GRANT ALL ON *.* to stack@'%' IDENTIFIED BY 'devstack'"
mysql -u root -e "FLUSH PRIVILEGES"

# removes the local default binding
sed -i '/bind-address/s/^/#/' /etc/mysql/my.cnf


# restarts the server
/etc/init.d/mysql restart
