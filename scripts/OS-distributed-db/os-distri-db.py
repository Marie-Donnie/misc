import os, sys
import execo as ex
import execo_g5k as ex5
from execo_g5k import oar
import time
from execo.time_utils import *
from execo.process import *
import traceback


plan = ex5.planning
grid = ex5.oargrid
ky = ex5.kadeploy

okay = ["paravance","grisou","graphene","griffon"]
exclu = ex5.api_utils.get_g5k_clusters()
# list that contains all clusters excepts those in okay list
excluded = [c for c in exclu if c not in okay]

end = ex.time_utils.format_date(time.time()+1800)

# must have a .env on the frontend that will deploy the ubuntu 
envfile = "envdb/monubuntu.env"

try:
    # makes a reservation
    print("Making a reservation")
    planning = plan.get_planning(endtime=end)
    slots = plan.compute_slots(planning, walltime="00:15:00", excluded_elements=excluded)
    startdate, enddate, resources = plan.find_free_slot(slots, {'grid5000':3})                    
    resources = plan.distribute_hosts(resources, {'grid5000':3}, excluded_elements=excluded)
    if startdate is None:
        raise ReservationError("Could not find a slot for the requested resources.")
    specs = plan.get_jobs_specs(resources, excluded_elements=excluded)
    # print("Using sites : %s" % resources)
    subs, _ = grid.oargridsub(specs, walltime="00:15:00", job_type='deploy')
    if subs is None:
        raise ReservationError("No oargrid job was created.")
    else:
        print("Using new oargrid job : %s" % subs)
    jobs = grid.get_oargrid_job_oar_jobs(subs)
    nodes = grid.get_oargrid_job_nodes(subs)
    for job in jobs:
        print("Job id : %s, site : %s" % (job[0], job[1]))
    print("Using nodes : %s" % nodes)

    # deploys
    print("Deploying ubuntu on nodes")
    deployment = ky.Deployment(hosts=nodes, env_file=envfile)
    deployed_hosts, _ = ky.deploy(deployment)
    print("Deployed on %s" % deployed_hosts)
    if len(deployed_hosts) == 0:
        raise DeploymentError("Error while deploying")      
    ex.action.Remote("git clone https://github.com/Marie-Donnie/discovery-vagrant.git", nodes[0], connection_params={'user':'ci'}).run()
    print("Deploying discovery devstack")
    ex.action.Remote("cd discovery-vagrant ; ./deploy.sh", node[0], connection_params={'user':'ci'}).run()
    
except Exception as e:
    t, value, tb = sys.exc_info()
    print str(t) + " " + str(value)
    traceback.print_tb(tb)
    


