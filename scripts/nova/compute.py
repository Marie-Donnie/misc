# Script that analyses the results

import json
import pandas as pd
import matplotlib.pyplot as plt

with open("/opt/logs/db_api_disco.json", "r") as discojson:
    with open("/opt/logs/db_api_mysql.json", "r") as mysqljson:
        ddicts = json.load(discojson)
        mdicts = json.load(mysqljson)
        ddf = pd.DataFrame(ddicts)
        mdf = pd.DataFrame(mdicts)
        # print(df)                  
        # print(df.describe())
        dduree = ddf.groupby("method").mean()
        mduree = mdf.groupby("method").mean()
        dduree2 = dduree.loc[:,["duration"]]
        mduree2 = mduree.loc[:,["duration"]]
        # print(duree2)
        # duree2.plot.bar()
        # plt.show()
        # pduree = pd.merge(dduree2, mduree2, how='right')
        # print(mduree)
        # print(dduree)
        dduree2.columns = ['disco']
        mduree2.columns = ['mysql']
        pduree = mduree2.join(dduree2)
        print(pduree)
        pduree.plot.bar(stacked=True)
        plt.show()
