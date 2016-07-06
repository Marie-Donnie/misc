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
    -i <impl>          Choose implementation (disco or mysql)
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

disco_vagrant = "https://github.com/Marie-Donnie/discovery-vagrant.git"
o_s_d = "https://raw.githubusercontent.com/Marie-Donnie/misc/master/scripts/OS-distributed-db/"

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
                self.deploy_ubuntu()
                self._preparation(impl)
                self._deploy_disco_vag()
                self._rally()
                self._get_files()
                    
        except Exception as e:
            t, value, tb = sys.exc_info()
            print str(t) + " " + str(value)
            traceback.print_tb(tb)
            logger.info(__doc__)

            
    def deploy_ubuntu(self):
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

            
    def _preparation(self, impl="disco"):
        # prepare disco-vagrant
        self.main = self.nodes[0]
        self.db = self.nodes[1]
        logger.info("Discovery-vagrant will deploy on : %s, for %s implementation" % (self.main, impl))
        logger.info("The databases will be stored on : %s" % self.db)

        # get the ips for the database and store them into a file
        ifconfig = ex.process.SshProcess("ifconfig eth0", self.db, connection_params={'user':'ci'})
        ifconfig.run()
        with open("ip.txt", "w") as ipfile:
            ipfile.write(ifconfig.stdout)
        logger.info("Ip stored")

        # copie the file to the self.main vm
        ex.action.Put([self.main], ["ip.txt"], connection_params={'user':'ci'}).run()
        logger.info("Ip file copied")

        # set a list of tuples with commands to execute, the node where it will be executed and a log info
        commands = [
            ("git clone -b my-versions "+disco_vagrant, self.main, "Cloning disco-vagrant"),
            ("wget "+o_s_d+"changeip.sh", self.main, "Downloading changeip.sh"),
            ("chmod +x changeip.sh ; ./changeip.sh ip.txt", self.main, "Changing permissions of changeip.sh"),
            ("wget "+o_s_d+"db-access.sh", self.db, "Downloading db-access.sh"),
            ("chmod +x db-access.sh ; sudo ./db-access.sh", self.db, "Changing permissions of db-access.sh")
        ]

        # change the branch to download for mysql
        if (impl=="mysql"):
            commands.append(("cd discovery-vagrant ; sed -i 's/NOVA_BRANCH=disco\/mitaka/NOVA_BRANCH=vanilla/' 05_devstack.sh", self.main, "Changing implementation to mysql"))

        # execute all commands
        for line in commands:
            command = line[0]
            machine = line[1]
            log = line[2]
            self._exec_on_node(command, machine, log)

    def _exec_on_node(self, command, machine, log):
        logger.info(log)
        rem = ex.action.Remote(command, machine, connection_params={'user':'ci'}).run()
        if rem.ok :
            logger.info("Success")
        else:
            logger.info("Failure")

    def _deploy_disco_vag(self):        
        # use discovery-vagrant with remote databases and all the tweaks above
        logger.info("Deploying discovery devstack")
        ex.action.Remote("cd discovery-vagrant ; ./deploy.sh", self.main, connection_params={'user':'ci'}).run()
        logger.info("Disco OS deployed")

    def _rally(self):    
        # clone repository
        logger.info("Cloning rally-vagrant...")
        ex.action.Remote("git clone https://github.com/BeyondTheClouds/rally-vagrant.git", self.main, connection_params={'user':'ci'}).run()
        logger.info("Done")
        # launch the tests        
        logger.info("Executing tests")
        ex.action.Remote("cd rally-vagrant ; python rally-g5k.py config.json /home/ci/jenkins/workspace/Rally-G5k/rally/samples/tasks/scenarios/nova/create-and-delete-floating-ips-bulk.json", self.main, connection_params={'user':'ci'}).run()
        logger.info("Tests finished")

    def _get_files(self):
        cmd = "sudo su root ; mkdir /vagrant/logs ; cp /opt/logs/db_api_*.log /vagrant/logs/"
        # get back the json file from discovery-vagrant (since the folder is linked to VBox /vagrant)
        self._exec_on_node("cd discovery-vagrant ; vagrant ssh pop0 -c "+cmd, self.main, "Changing the logs directory")

        path = "/home/ci/discovery-vagrant/logs/db_api_" + impl + ".log"
        ex.action.Get(self.main, [path], local_location="./results", connection_params={'user':'ci'}).run()
        logger.info("Got file %s" % path)

        os.remove("ip.txt")
        logger.info("Files removed")
    
    # gets the results
    # logger.info("Analyzing the results")    
    # ex.action.Remote("git clone https://github.com/Marie-Donnie/misc.git", self.main, connection_params={'user':'ci'}).run()
    # ex.action.Remote("cd misc/scripts/nova/ ; chmod +x analyse.sh ; ./analyse.sh", db, connection_params={'user':'ci'}).run()
    # logger.info("Done")



if __name__ == "__main__":
    engine = os_distri_db()
    engine.run()



    


