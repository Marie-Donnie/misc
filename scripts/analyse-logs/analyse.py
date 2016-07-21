"""Runs an analysis of logs

Usage:
    analyse.py (--path=<path>)(-d | -m | -d -m)
    analyse.py [-h | --help]
    analyse.py --version

Options:
    -h --help        Show this screen.
    --version        Show version.
    --path=<path>    Path to discovery and/or mysql file(s)
    -d               Use discovery file
    -m               Use mysql file

"""
import json
import os
import pandas as pd
from docopt import docopt


class analyse():

    def __init__(self):
        """Define options"""
        self.argus = docopt(__doc__, version = 'Analyse 2.0')
        # print(self.argus)
        self.disco = 'db_api_disco'
        self.mysql = 'db_api_mysql'
        self.path = self.argus["--path"]
        self.files = []

        if self.argus['-m']:
            self.files.append(self.mysql)
        if self.argus['-d']:
            self.files.append(self.disco)
        print(self.files)

    def run(self):
        # for impl in self.files: 
        self.resultsjson()
        self.compute()

    def resultsjson(self):
        for f in self.files:
            f += '.log'
            f = self.path + f
            if not os.path.isfile(f):
                print("Path %s is not correct" % f)
            else:
                with open(f, "r") as logs:
                    # put each lines into a list
                    lines = logs.readlines()
                    # remove the nasty new lines
                    lines = map(lambda s: s.replace('\n',''), lines)
                    # decode each elements of the list
                    dicts = map(json.loads, lines)
                    # encode the list
                    with open(os.path.splitext(f)[0] + '.json',"w") as fjson:
                        fjson.write(json.dumps(dicts, indent=4))

    def compute(self):
        i = 0
        dicts = []
        df = []
        duree = []
        duree2 = []
        for impl in self.files :
            impljson = impl + '.json'
            if os.path.isfile(self.path + impljson):
                print(impljson)
                with open(self.path + impljson, "r") as fileopen:                    
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
        # chemin = os.path.dirname(os.path.realpath(__file__))
        with open(self.path+"/results.txt","w") as results:
            results.write(pduree.to_string())
            results.write("\n")
            print("File written")
            # testing functions, uncomment also matplotlib import to use it
            # print(pduree)
            # pduree.plot.bar(stacked=True)
            # plt.show()   


        
if __name__ == '__main__':
    engine = analyse()
    engine.run()
