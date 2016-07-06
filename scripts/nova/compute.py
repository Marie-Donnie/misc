# Script that analyses the results
"""Compute results

Usage:
    compute.py <disco> <mysql>
    compute.py [-h | --help]
    compute.py --version

Options:
    -h --help     Show this screen.
    --version     Show version.
    disco         Path to disco file
    mysql         Path fo mysql file

"""

import json
import pandas as pd
import matplotlib.pyplot as pl
import os
from docopt import docopt

class compute():

    def __init__(self):
        """Define options"""
        argus = docopt(__doc__, version = 'Compute 2.0')
        #print(argus)
        if "db_api_disco.json" in argus["<disco>"]:
            self.disco = argus["<disco>"]
        if "db_api_mysql.json" in argus["<mysql>"]:
            self.mysql = argus["<mysql>"]        

    def run(self):
        print("Using file %s for discovery implementation" % self.disco)
        print("Using file %s for mysql implementation" % self.mysql)

        with open(self.disco, "r") as discojson:
            with open(self.mysql, "r") as mysqljson:
                # deserialize files
                ddicts = json.load(discojson)
                mdicts = json.load(mysqljson)
                # create pandas dataframes
                ddf = pd.DataFrame(ddicts)
                mdf = pd.DataFrame(mdicts)
                # group by method and calculate the average duration
                dduree = ddf.groupby("method").mean()
                mduree = mdf.groupby("method").mean()
                # keep only duration, remove timestamp
                dduree2 = dduree.loc[:,["duration"]]
                mduree2 = mduree.loc[:,["duration"]]
                # rename the columns
                dduree2.columns = ['disco']
                mduree2.columns = ['mysql']
                # join the dataframes
                pduree = mduree2.join(dduree2)
                pduree["difference"] = pduree["disco"] - pduree["mysql"]
                # save the results
                chemin = os.path.dirname(os.path.realpath(__file__))
                with open(chemin+"/results.txt","w") as results:
                    results.write(pduree.to_string())
                    # testing functions
                    # print(pduree)
                    # pduree.plot.bar(stacked=True)
                    # plt.show()

        
if __name__ == '__main__':
    engine = compute()
    engine.run()
