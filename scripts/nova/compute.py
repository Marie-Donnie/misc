# Script that analyses the results

import json
import pandas as pd

with open("/opt/logs/db_api_mysql.json", "r") as fjson:
    dicts = json.load(fjson)
    df = pd.DataFrame(dicts)
    # print(df)                  
    # print(df.describe())
    print(df.groupby("method").mean())
