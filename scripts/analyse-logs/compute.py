# Script that analyses the results
"""Compute results

Usage:
    compute.py run (--path=<path>)(-d | -m | -d -m)
    compute.py [-h | --help]
    compute.py --version

Options:
    -h --help          Show this screen.
    --version          Show version.
    --disco=<disco>    Path to disco file
    --mysql=<mysql>    Path fo mysql file

"""

import json
import pandas as pd
#import matplotlib.pyplot as pl
import os
from docopt import docopt

class compute():

    def __init__(self):
        """Define options"""
        self.argus = docopt(__doc__, version = 'Compute 3.0')
        # print(self.argus)
        
        self.disco = 'db_api_disco.json'
        self.mysql = 'db_api_mysql.json'
        self.path = self.argus["--path"]
        self.files = []

        if self.argus['-m']:
            self.files.append(self.mysql)
            print("Using file %s%s for mysql implementation" % (self.path, self.mysql))
        if self.argus['-d']:
            self.files.append(self.disco)
            print("Using file %s%s for discovery implementation" % (self.path, self.disco))
        print(self.files)

    def run(self):
        i = 0
        dicts = []
        df = []
        duree = []
        duree2 = []
        for impl in self.files :
            if os.path.isfile(self.path + impl):
                print(impl)
                with open(self.path + impl, "r") as fileopen:                    
                    # deserialize files
                    dicts.append(json.load(fileopen))
                    # create pandas dataframes
                    df.append(pd.DataFrame(dicts[i]))
                    # group by method and calculate the average duration
                    duree.append(df[i].groupby("method").mean())
                    # keep only duration, remove timestamp
                    duree2.append(duree[i].loc[:,["duration"]])
                    # rename the columns
                    if (impl == self.disco):
                        duree2[i].columns = ["disco"]
                    else:
                        duree2[i].columns = ["mysql"]
                i += 1
            else:
                print("Path not correct")
                exit()

        if len(self.files) == 2:
            pduree = duree2[0].join(duree2[1])
            pduree["difference"] = pduree["disco"] - pduree["mysql"]
        else:
            pduree = duree2[0]

        # save the results
        chemin = os.path.dirname(os.path.realpath(__file__))
        with open(chemin+"/results.txt","w") as results:
            results.write(pduree.to_string())
        print("File written")
            # testing functions, uncomment also matplotlib import to use it
            # print(pduree)
            # pduree.plot.bar(stacked=True)
            # plt.show()   


        
if __name__ == '__main__':
    engine = compute()
    engine.run()
