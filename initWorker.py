import os, sys, subprocess
from novaclient.client import Client

def substitute_line(new, old, file):
    f = open(file, "r")
    lines = f.readlines()
    f.close()

    f = open(file, "w")
    for line in lines:
            if not old in line:
                    f.write(line)
            else:
                    f.write(new + '\n')
    f.close()

# Create instance
def init_n(worker_number, nc):
    worker_name = "mat_test_%i" %(worker_number)
    import time 
    #image = nc.images.find(name="Ubuntu Server 14.04 LTS (Trusty Tahr)")
    image = nc.images.find(id='59a19f79-f906-44e0-964a-22d66558cc54')
    flavor = nc.flavors.find(name="m1.medium")
    network = nc.networks.find(label="ACC-Course-net")
    keypair = nc.keypairs.find(name="mathieukeypair")
    ud = open('userdata2.yml', 'r')
    nc.keypairs.list()
    #f = open('cloud.key.pub','r')
    #publickey = f.readline()[:-1]
    #keypair = nc.keypairs.create('mathieukeypair',publickey)
    #f.close()
    server = nc.servers.create(name = worker_name ,image = image.id,flavor = flavor.id,network = network.id,
     key_name = keypair.name, userdata = ud)

def init(w_left, number_of_workers):
    config = {'username':os.environ['OS_USERNAME'],
        'api_key':os.environ['OS_PASSWORD'],
        'project_id':os.environ['OS_TENANT_NAME'],
        'auth_url':os.environ['OS_AUTH_URL']}

    nc = Client('2',**config)

    BROKER_IP = subprocess.check_output("wget -qO- http://ipecho.net/plain ; echo", shell=True).rstrip()
    substitute_line('    - export BROKER_IP="' + BROKER_IP +'"', 'export BROKER_IP=', 'userdata2.yml')
    for i in range(w_left,number_of_workers):
        init_n(i, nc)

    return number_of_workers

def kill_n(i, nc):
    toTerminate = "mat_test_%i" %(i)
    serverToTerminate = nc.servers.find(name=toTerminate)
    serverToTerminate.delete()
    print("killed instance: %s" %(toTerminate))

def kill(w_left, number_of_workers):
    config = {'username':os.environ['OS_USERNAME'], 
          'api_key':os.environ['OS_PASSWORD'],
          'project_id':os.environ['OS_TENANT_NAME'],
          'auth_url':os.environ['OS_AUTH_URL'],
          }
    nc = Client('2',**config)
    subprocess.check_call("sudo rabbitmqctl stop_app", shell=True)
    subprocess.check_call("sudo rabbitmqctl force_reset", shell=True)
    for i in range(w_left,number_of_workers):
        kill_n(i, nc)
    
    subprocess.check_call("sudo rabbitmqctl start_app", shell=True)
    subprocess.check_call("sudo rabbitmqctl add_user ma fu", shell=True)
    subprocess.check_call("sudo rabbitmqctl add_vhost mafu", shell=True)
    subprocess.check_call('sudo rabbitmqctl set_permissions -p mafu ma ".*" ".*" ".*"', shell=True)
    return w_left

# Terminate all your running instances