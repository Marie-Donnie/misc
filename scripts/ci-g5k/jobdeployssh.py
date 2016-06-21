import os, sys
import execo as ex
import execo_g5k as ex5
from execo_g5k import oar
import time
from execo.time_utils import *
from execo.process import *
import traceback


plan = ex5.planning
okay = ["paravance","grisou","graphene","griffon"]
exclu = ex5.api_utils.get_g5k_clusters()
excluded = [c for c in exclu if c not in okay]

end = ex.time_utils.format_date(time.time()+12600)
envfile = "env/monubuntu.env"

try:
    # makes a reservation
    print("Making a reservation")
    planning = plan.get_planning(endtime=end)
    slots = plan.compute_slots(planning, walltime="03:00:00", excluded_elements=excluded)
    startdate, enddate, resources = plan.find_free_slot(slots, {'grid5000':1})                    
    resources = plan.distribute_hosts(resources, {'grid5000':1}, excluded_elements=excluded)
    specs = plan.get_jobs_specs(resources, excluded_elements=excluded)
    sub, site = specs[0]
    sub.additional_options = "-t deploy"
    sub.reservation_date = startdate
    sub.walltime = "03:00:00"
    job = ex5.oarsub([(sub, site)])
    job_id = job[0][0]
    job_site = job[0][1]
    host = ex5.get_oar_job_nodes(job_id, job_site)
    
except Exception as e:
    t, value, tb = sys.exc_info()
    print str(t) + " " + str(value)
    traceback.print_tb(tb)

try:
    # deploys
    print("Deploying monubuntu at " + job_site)
    deployment = ex5.kadeploy.Deployment(hosts=host, env_file=envfile)
    deployed_hosts, _ = ex5.deploy(deployment)
    # print("Deployed on " + deployed_host[0])
    
    if len(deployed_hosts) != 0:
        # gets the agent started, starting by downloading it
        print("Downloading and launching the slave agent")
        ex.action.Remote("wget https://ci.inria.fr/beyondtheclouds/jnlpJars/slave.jar", deployed_hosts, connection_params={'user':'ci'}).run()
        # replaces the process with the ssh connection and the launching of the slave agent
        os.execl("/usr/bin/ssh", "/usr/bin/ssh", "ci@"+list(deployed_hosts)[0], "java -jar /home/ci/slave.jar")
        
    else:
        raise DeploymentError("Error while deploying")

except Exception as e:
    t, value, tb = sys.exc_info()
    print str(t) + " " + str(value)
    traceback.print_tb(tb)
    delete = ex5.oar.oardel(job_id, job_site)
    print("Job deleted")
