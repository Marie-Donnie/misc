# Script to get the logs from lines of json to a global json format

import json
import sys, os



def resultsjson(args):
    for f in args:
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
                

if __name__ == '__main__':
    # argus = sys.argv
    # del argus[0]
    resultsjson(argus)
