"""Argus.

Usage:
    os-distri-db.py reservation
    os-distri-db.py run (--full | -i <impl>)
    os-distri-db.py (-h | --help)
    os-distri-db.py --version

Options:
    -h --help     Show this screen
    --version     Show version
    --full        Run tests for both implementation
    -i <impl>     Choose implementation 


"""

import os, sys
import time
import traceback
import execo as ex
import execo_g5k as ex5
from execo_g5k import oar
from execo_engine import logger
from execo.time_utils import *
from execo.process import *
from docopt import docopt

plan = ex5.planning
ky = ex5.kadeploy


end = ex.time_utils.format_date(time.time()+11000)

# must have a .env on the frontend that will deploy the ubuntu 
envfile = "envdb/monubuntu.env"

class os-distri-db():

    def __init__(self):
        """Define options for the experiment"""
        argus = docopt(__doc__, version = 'Deployments 1.0')
        print(argus)

        self.resa_only = False
        self.implementation = []
        if argus["--full"]:
            self.implementation = ["disco", "mysql"]
        else:
            if argus["-i"]:
                self.implementation = [argus["-i"]]
            else:
                self.resa_only = True
        print(self.resa_only)
        print(self.implementation)

    def run(self):
        """Perform experiment"""
        print("Options : %s" % self.options)

            
        try:
            # makes a reservation                                 
            logger.info("Making a reservation")
            job = ex5.oarsub([( ex5.OarSubmission(resources = "/cluster=1/nodes=2", walltime="03:00:00", job_type='deploy'), "rennes")])
            job_id, site = job[0]
            if job_id is None:
                raise ValueError("Could not find a slot for the requested resources.")
            logger.info("Using new oar job : %s, on site : %s" % (job_id, site))
            logger.info("Waiting for job to start")
            nodes = ex5.get_oar_job_nodes(job_id, site)
            logger.info("Using nodes : %s" % nodes)
            logger.info("Reservation done")
            
        except Exception as e:
            t, value, tb = sys.exc_info()
            print str(t) + " " + str(value)
            traceback.print_tb(tb)

        try:
            if not self.resa_only:
                for impl in self.implementation:
                    print(impl)
                    if impl not in {"mysql", "disco"}:
                        raise ValueError("Use only mysql or disco arguments")
                    self.deploys()
                    self._disco_vag(impl)
                    
        except Exception as e:
            t, value, tb = sys.exc_info()
            print str(t) + " " + str(value)
            traceback.print_tb(tb)
            
    def deploys(self):
        # deploys
        logger.info("Deploying ubuntu on nodes")
        deployment = ky.Deployment(hosts=nodes, env_file=envfile)
        deployed_hosts, _ = ky.deploy(deployment)
        logger.info("Deployed on %s" % deployed_hosts)
        if len(deployed_hosts) == 0:
            raise DeploymentError("Error while deploying")

    def _disco_vag(self, impl="disco"):
        # prepares disco-vagrant
        main = nodes[0]
        db = nodes[1]
        logger.info("Discovery-vagrant will deploy on : %s, for %s implementation" % (main, impl)
        logger.info("The databases will be stored on : %s" % db)

        # gets the ips for the database and stores them into a file
        ifconfig = ex.process.SshProcess("ifconfig eth0", db, connection_params={'user':'ci'})
        ifconfig.run()
        with open("ip.txt", "a") as ipfile:
            ipfile.write(ifconfig.stdout)
        logger.info("Ip stored")
                    
        # copies the file to the main vm
        ex.action.Put([main], ["ip.txt"], connection_params={'user':'ci'}).run()
        logger.info("File copied")
        ex.action.Remote("git clone https://github.com/Marie-Donnie/discovery-vagrant.git", main, connection_params={'user':'ci'}).run()
        logger.info("Discovery-Vagrant cloned")
        # handles the scripts, gives access to the databases
        ex.action.Remote("wget https://raw.githubusercontent.com/Marie-Donnie/misc/master/scripts/OS-distributed-db/changeip.sh", main, connection_params={'user':'ci'}).run()
        ex.action.Remote("wget https://raw.githubusercontent.com/Marie-Donnie/misc/master/scripts/OS-distributed-db/db-access.sh", db, connection_params={'user':'ci'}).run()    
        logger.info("Scripts downloaded")
        ex.action.Remote("chmod +x changeip.sh ; ./changeip.sh ip.txt", main, connection_params={'user':'ci'}).run()
        ex.action.Remote("chmod +x db-access.sh ; sudo ./db-access.sh", db, connection_params={'user':'ci'}).run()

        # make some changes for discovery-vagrant, since default uses ROME
        if (impl="mysql"):
            logger.info("Adjusting deployment for mysql")
            ex.action.Remote("cd discovery-vagrant ; sed -i 's/NOVA_BRANCH=disco\/mitaka/NOVA_BRANCH=vanilla/' 05_devstack.sh", main, connection_params={'user':'ci'}).run()   

        # uses discovery-vagrant with remote databases
        logger.info("Deploying discovery devstack")
        ex.action.Remote("cd discovery-vagrant ; ./deploy.sh", main, connection_params={'user':'ci'}).run()
        logger.info("Disco OS deployed")

        # launches the tests
        logger.info("Cloning rally-vagrant...")
        ex.action.Remote("git clone https://github.com/BeyondTheClouds/rally-vagrant.git", main, connection_params={'user':'ci'}).run()
        logger.info("Done")
        logger.info("Executing tests")
        ex.action.Remote("cd rally-vagrant ; python rally-g5k.py config.json /home/ci/jenkins/workspace/Rally-G5k/rally/samples/tasks/scenarios/nova/create-and-delete-floating-ips-bulk.json", main, connection_params={'user':'ci'}).run()
        logger.info("Tests finished")

   
        # path = "/opt/logs/db_api_" + impl
        # ex.action.Get(main, path, local_location="./results", connection_params={'user':'ci'})

    
    # gets the results
    # logger.info("Analyzing the results")    
    # ex.action.Remote("git clone https://github.com/Marie-Donnie/misc.git", main, connection_params={'user':'ci'}).run()
    # ex.action.Remote("cd misc/scripts/nova/ ; chmod +x analyse.sh ; ./analyse.sh", db, connection_params={'user':'ci'}).run()
    # logger.info("Done")
    
    
    os.remove("ip.txt")
    logger.info("Files removed")
    
except Exception as e:
    t, value, tb = sys.exc_info()
    print str(t) + " " + str(value)
    traceback.print_tb(tb)
    


