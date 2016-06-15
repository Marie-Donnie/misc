import json

with open("/opt/logs/db_api.log", "r") as logs:
    lines = logs.readlines()
    lines = map(lambda s: s.replace('\n',''), lines)
    #print(lines)
    dicts = map(json.loads, lines)
    with open("/opt/logs/db_api.json","w") as fjson:
        fjson.write(json.dumps(dicts))
