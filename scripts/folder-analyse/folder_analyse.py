"""Search a folder for experiment results and analyse them. 

Usage:
    folder_analyse.py run <directory>
    folder_analyse.py (-h | --help)
    folder_analyse.py --version

Options:
    -h --help          Show this screen
    --version          Show version
    <directory>        Specify the folder to analyse

"""

import os, sys
import json
import time
import traceback
import pandas as pd
from docopt import docopt

class folder_analyse():

    def __init__(self):
        """Define options for the analyse"""
        argus = docopt(__doc__, version = 'Analyse folder 1.0')
        self.directory = argus["<directory>"]
        print(argus)

    def run(self):
        self.disco = []
        self.mysql = []
        try:
            for path, folders, files in os.walk(self.directory):
                for file in files:
                    # with open("average.txt", "w") as average:
                    #     average.write(ifconfig.stdout)
                    if "db_api_disco.json" in file:
                        self.disco.append(os.path.join(path,file))
                    else:
                        if "db_api_mysql.json" in file:
                            self.mysql.append(os.path.join(path,file))
            
        except Exception as e:
            t, value, tb = sys.exc_info()
            print str(t) + " " + str(value)
            traceback.print_tb(tb)
            print(__doc__)
            sys.exit(3)

        mean_disco = self._analyse(self.disco, "disco")
        mean_mysql = self._analyse(self.mysql, "mysql")

        
        # mean = pd.concat([mean_mysql,mean_disco])
        # mean["difference"] = mean["disco"] - mean["mysql"]

            
    def _analyse(self, file_list, name):
        i = 0
        dicts = []
        df = []
        duree = []
        duree2 = []

        for f in file_list:
            with open(f, "r") as fileopen:                    
                # deserialize files
                dicts.append(json.load(fileopen))
                # create pandas dataframes
                df.append(pd.DataFrame(dicts[i]))
                # group by method and calculate the average duration
                duree.append(df[i].groupby("method").mean())
                # keep only duration, remove timestamp
                duree2.append(duree[i].loc[:,["duration"]])
                # rename the columns
                duree2[i].columns = [name]
                i += 1
                pduree = pd.concat(duree2, axis=1)
                means = pduree.mean(axis=1)
            
        # save the results
        # chemin = os.path.dirname(os.path.realpath(__file__))
        with open("results-%s.txt" %name,"w") as results:
            results.write("Using %d results\n" % len(file_list))
            results.write(means.to_string())
            results.write("\n")
        print("File written")

        return means

if __name__ == "__main__":
    engine = folder_analyse()
    engine.run()
