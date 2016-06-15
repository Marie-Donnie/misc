#!/bin/bash

current=$(dirname $0)
dir="/opt/logs/"
mysql="db_api_mysql"
disco="db_api_disco"

python $current/resultsjson.py $dir$mysql.log $dir$disco.log
python $current/compute.py
