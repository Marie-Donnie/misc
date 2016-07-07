#!/bin/bash

# get the name of current directory
current=$(dirname $0)

# print the help
if [ "$1" == "-h" ]; then
  echo "Usage: `basename $0` path-to-log-files"
  exit 0
fi

# define the variables
dir=$1
disco="db_api_disco"
mysql="db_api_mysql"

# run the scripts
python $current/resultsjson.py $dir$disco.log $dir$mysql.log
python $current/compute.py run --path $dir -m -d
