# Script that analyses the results

import json
import pandas as pd
import matplotlib.pyplot as pl
import os 


with open("/opt/logs/db_api_disco.json", "r") as discojson:
    with open("/opt/logs/db_api_mysql.json", "r") as mysqljson:
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
