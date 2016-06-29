## OpenStack with remote databases on Grid'5000

### What it does

This script gets 3 nodes on either paravance, grisou, graphene or griffon clusters on Grid'5000.

It deploys ubuntudb.tgz, which is the same as ubuntu.tgz ([cf ci-g5k Readme](https://github.com/Marie-Donnie/misc/tree/master/scripts/ci-g5k "ci-g5k")), but with a redis and mysql databases ready to be used.

Then, on the "main" node, it deploys my discovery-vagrant, with the necessary tweaking to connect to the other two nodes databases.

![alt text](requetes.png "What it does sketch")

### What you need

You will need to get the kadeploy environnement file and the tarball in a envdb folder on Rennes, Nancy and Grenoble frontends.

Finally, with `os-distri-db.py` on the frontend you wish to use, run the command :
```
python os-distri-db.py
```
