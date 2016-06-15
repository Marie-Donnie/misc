#!/bin/bash

current=$(dirname $0)

python $current/resultsjson.py /opt/logs/db_api_mysql.log /opt/logs/db_api_disco.log
