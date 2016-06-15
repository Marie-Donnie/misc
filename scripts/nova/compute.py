# Script that analyses the results

import json
import pandas as pd
import matplotlib.pyplot as plt

with open("/opt/logs/db_api_disco.json", "r") as fjson:
    dicts = json.load(fjson)
    df = pd.DataFrame(dicts)
    # print(df)                  
    # print(df.describe())
    duree = df.groupby("method").mean()
    duree2 = duree.loc[:,["duration"]]
    print(duree2)
    duree2.plot.bar()
    plt.show()
