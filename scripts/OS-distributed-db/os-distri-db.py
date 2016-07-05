"""Openstack with distributed databases

Usage:
    os-distri-db.py reservation [--site <city>]
    os-distri-db.py reservation [--duration <time>]
    os-distri-db.py reservation [--nodes <nb>]
    os-distri-db.py reservation --only
    os-distri-db.py run [(--job_id <id> --job_site <city>)(--full | -i <impl>)]
    os-distri-db.py (-h | --help)
    os-distri-db.py --version

Options:
    -h --help          Show this screen
    --version          Show version
    --site <city>      Choose the site [default: rennes]
    --duration <time>  A duration, formatted hh:mm:ss, must be <= to [default: 03:00:00]
    --nodes <nb>       Number of nodes [default: 2]
    --full             Run tests for both implementation
    -i <impl>          Choose implementation 
    --job_id <id>      Specify the job id of an already created job
    --job_site <city>  Specify the job site of an already created job


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

class os_distri_db():

    def __init__(self):
        """Define options for the experiment"""
        argus = docopt(__doc__, version = 'Deployments 1.0')
        print(argus)

        self.resa_only = argus["--only"]
        self.machines = argus["--nodes"]
        self.duration = argus["--duration"]
        self.site = argus["--site"]
        self.job_id = argus["--job_id"]
        self.job_site = argus["--job_site"]
        self.implementation = []
        if argus["--full"]:
            self.implementation = ["disco", "mysql"]
        else:
            if argus["-i"]:
                self.implementation = [argus["-i"]]

    def run(self):
        """Perform experiment"""
        
        try:
            if self.job_id is None:
                # make a reservation                                 
                logger.info("Making a reservation for %s nodes, on site: %s, during %s" % (str(self.machines), self.site, self.duration))
                job = ex5.oarsub([( ex5.OarSubmission(resources = "/cluster=1/nodes="+str(self.machines), walltime=self.duration, job_type='deploy'), self.site)])
                job_id, site = job[0]
                if job_id is None:
                    raise ValueError("Could not find a slot for the requested resources.")
                logger.info("Using new oar job : %s, on site : %s" % (job_id, site))
                logger.info("Waiting for job to start")
                self.nodes = ex5.get_oar_job_nodes(job_id, site)
                logger.info("Reservation done")
                if self.resa_only:
                    exit
            else:
                if self.job_id.isdigit():
                    self.nodes = ex5.get_oar_job_nodes(int(self.job_id), self.job_site)
                else:
                    raise ValueError("Use a number for job id")
            logger.info("Using nodes : %s" % self.nodes)
            
        except Exception as e:
            t, value, tb = sys.exc_info()
            print str(t) + " " + str(value)
            traceback.print_tb(tb)
            logger.info(__doc__)

        try:
            for impl in self.implementation:
                logger.info("Using %s for implementation" % impl)
                if impl not in {"mysql", "disco"}:
                    raise ValueError("Use only mysql or disco arguments")                    
                self.deploys()
                self._disco_vag(impl)

                    
        except Exception as e:
            t, value, tb = sys.exc_info()
            print str(t) + " " + str(value)
            traceback.print_tb(tb)
            logger.info(__doc__)

            
    def deploys(self):
        # deploy
        try:
            logger.info("Deploying ubuntu on nodes")
            deployment = ky.Deployment(hosts=self.nodes, env_file=envfile)
            deployed_hosts, _ = ky.deploy(deployment, check_deployed_command=False)
            logger.info("Deployed on %s" % deployed_hosts)
            if len(deployed_hosts) == 0:
                raise ValueError("Error while deploying the environment file")
            
        except Exception as e:
            t, value, tb = sys.exc_info()
            print str(t) + " " + str(value)
            traceback.print_tb(tb)

            
    def _disco_vag(self, impl="disco"):
        # prepare disco-vagrant
        main = self.nodes[0]
        db = self.nodes[1]
        logger.info("Discovery-vagrant will deploy on : %s, for %s implementation" % (main, impl))
        logger.info("The databases will be stored on : %s" % db)

        # get the ips for the database and store them into a file
        ifconfig = ex.process.SshProcess("ifconfig eth0", db, connection_params={'user':'ci'})
        ifconfig.run()
        with open("ip.txt", "a") as ipfile:
            ipfile.write(ifconfig.stdout)
        logger.info("Ip stored")
                    
        # copie the file to the main vm
        ex.action.Put([main], ["ip.txt"], connection_params={'user':'ci'}).run()
        logger.info("Ip file copied")
        ex.action.Remote("git clone -b my-versions https://github.com/Marie-Donnie/discovery-vagrant.git", main, connection_params={'user':'ci'}).run()
        logger.info("Discovery-Vagrant cloned")
        # handle the scripts, give access to the databases
        ex.action.Remote("wget https://raw.githubusercontent.com/Marie-Donnie/misc/master/scripts/OS-distributed-db/changeip.sh", main, connection_params={'user':'ci'}).run()
        ex.action.Remote("wget https://raw.githubusercontent.com/Marie-Donnie/misc/master/scripts/OS-distributed-db/db-access.sh", db, connection_params={'user':'ci'}).run()    
        logger.info("Scripts downloaded")
        ex.action.Remote("chmod +x changeip.sh ; ./changeip.sh ip.txt", main, connection_params={'user':'ci'}).run()
        ex.action.Remote("chmod +x db-access.sh ; sudo ./db-access.sh", db, connection_params={'user':'ci'}).run()
        ex.action.Remote("cd discovery-vagrant ; sed -i 's/NOVA_BRANCH=disco\/mitaka/&-vagrant/' 05_devstack.sh", main, connection_params={'user':'ci'}).run()
        ex.action.Remote("sed -i 's/chmod -R a+w \/opt\/logs/&\nmkdir \/vagrant\/logs\nchown stack:stack \/vagrant\/logs\nchmod -R a+w \/vagrant\/logs/' 02_rome.sh", main, connection_params={'user':'root'}).run()
        # make some changes for discovery-vagrant, since default uses ROME
        if (impl=="mysql"):
            logger.info("Adjusting deployment for mysql")
            ex.action.Remote("cd discovery-vagrant ; sed -i 's/NOVA_BRANCH=disco\/mitaka/NOVA_BRANCH=vanilla/' 05_devstack.sh", main, connection_params={'user':'ci'}).run()

        # use discovery-vagrant with remote databases
        logger.info("Deploying discovery devstack")
        ex.action.Remote("cd discovery-vagrant ; ./deploy.sh", main, connection_params={'user':'ci'}).run()
        logger.info("Disco OS deployed")

        
        # launch the tests
        logger.info("Cloning rally-vagrant...")
        ex.action.Remote("git clone https://github.com/BeyondTheClouds/rally-vagrant.git", main, connection_params={'user':'ci'}).run()
        logger.info("Done")
        logger.info("Executing tests")
        ex.action.Remote("cd rally-vagrant ; python rally-g5k.py config.json /home/ci/jenkins/workspace/Rally-G5k/rally/samples/tasks/scenarios/nova/create-and-delete-floating-ips-bulk.json", main, connection_params={'user':'ci'}).run()
        logger.info("Tests finished")

        # get back the json file
        path = "/home/ci/discovery-vagrant/db_api_" + impl + ".log"
        ex.action.Get(main, path, local_location="./results", connection_params={'user':'ci'}).run()
        logger.info("Got file %s" % path)

        os.remove("ip.txt")
        logger.info("Files removed")
    
    # gets the results
    # logger.info("Analyzing the results")    
    # ex.action.Remote("git clone https://github.com/Marie-Donnie/misc.git", main, connection_params={'user':'ci'}).run()
    # ex.action.Remote("cd misc/scripts/nova/ ; chmod +x analyse.sh ; ./analyse.sh", db, connection_params={'user':'ci'}).run()
    # logger.info("Done")



if __name__ == "__main__":
    engine = os_distri_db()
    engine.run()



    


