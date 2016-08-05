"""Wrapper for Rally to use with a Discovery Openstack deployed with Devstack

Usage:
    rally-disco-devstack.py ( --file=<file> | <file>... ) [-h | --help][--version]

Options:
    -h --help       Show this screen
    --version       Show version
    --file=<file>   Uses a file containing a list of scenarios

Arguments
    <file>          The scenarios Rally will use
"""

#!/usr/bin/env python

import traceback
import logging, time, datetime, signal
import os, sys, math
from time import sleep
import json
import re

from docopt import docopt


COLOR = '\033[94m'
ENDC = '\033[0m'

class rally_disco_devstack():

    def __init__(self):
            """Define options for the experiment"""
            self.argus = docopt(__doc__, version = 'Rally tests 2.0')
            print(self.argus)

    def run(self):
        """Perform experiment"""
        try :
            self.make_result_dir()
            self.benchmarking()
            
        except:
            print("Something went wrong")
            t, value, tb = sys.exc_info()
            print str(t) + " " + str(value)
            exit(3)

    def make_result_dir(self):
        # Make the directory for the results
        dt = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        self.result_dir = os.path.join(os.getcwd(), "results/%s" % dt)
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)


    def benchmarking(self):
        # Launch the benchmarks
        if self.argus['--file'] is not None:
            list_bench = self.argus['--file']
            if not os.path.isfile(list_bench):
                list_bench = os.path.join(os.getcwd(), self.argus['--file'])
            if os.path.isfile(list_bench):
                with open(list_bench, 'r') as bench_file:
                    benchmarks = [line.strip() for line in bench_file]
            else:
                print("Can't read %s" % self.argus['--file']) 
        else:
            benchmarks = self.argus['<file>']
    
        print(benchmarks)

        n_benchmarks = len(benchmarks)
        i_benchmark = 0
        for bench_file in benchmarks:
            if not os.path.isfile(bench_file):
                if not os.path.isfile(os.path.join(os.getcwd(), bench_file)):
                    print("Ignoring %s which is not a file" % bench_file)
                    continue
                else:
                    bench_file = os.path.join(os.getcwd(), bench_file)
                    
            i_benchmark += 1
            print("%s[%d/%d] Preparing benchmark %s %s" % (COLOR, i_benchmark, n_benchmarks, bench_file, ENDC))

            cmd = "rally task start %s" % (bench_file)
                                
            print("[%d/%d] Running benchmark %s" % (i_benchmark, n_benchmarks, bench_file))

            bench_basename = os.path.basename(bench_file)
                    
            # Execute rally task start
            rally_task = os.system(cmd)

            if rally_task != 0:
                print("Error while running benchmark")
                continue
            else:
                # Get the results back
                self.get_logs(bench_basename)

            print(COLOR+'----------------------------------------'+ENDC)

            
    def get_logs(self, bench_file):
        # Generate the HTML file
        print("Getting the results into " + self.result_dir)
        html_file = os.path.splitext(bench_file)[0] + '.html'
        dest = os.path.join(self.result_dir, html_file)
        result = os.system("rally task report --out=" + dest)
		
        if result != 0:
            print("Could not generate the HTML result file")

        else:
            print("Wrote " + dest)
            
        # Generate the XML file
        xml_file = os.path.splitext(bench_file)[0] + '.xml'
        dest = os.path.join(self.result_dir, xml_file)
        result = os.system("rally task report --junit --out=" + dest)

        if result != 0:
            print("Could not generate the XML result file")

        else:
            print("Wrote " + dest)

        # Get the metrics from Rally		
        metrics_file = os.path.join(self.result_dir, os.path.splitext(bench_file)[0] + '.json')
        result = os.system("rally task results")
                
        if result != 0:
            print("Could not get the metrics back")

        else:
            # The json is on the standard output of the process
            os.system("rally task results > %s" % metrics_file)
            print("Wrote " + metrics_file)


###################
###### Main #######
###################
if __name__ == "__main__":
	engine = rally_disco_devstack()
	engine.run()
