import os
import swiftclient.client

#uploads files to the container. 
#file_name is the name of the file and file_path is its location. 
def put_file(file_name, file_path):
    config = {'user':os.environ['OS_USERNAME'],
    'key':os.environ['OS_PASSWORD'],
   	'tenant_name':os.environ['OS_TENANT_NAME'],
   	'authurl':os.environ['OS_AUTH_URL']}

    conn = swiftclient.client.Connection(auth_version=2, **config)

    with open(file_path, 'r') as f:
        file_data = f.read()
    conn.put_object('matstorage', file_name, file_data)

#downloads files from the container. 
#file_name is the name of the file and file_path is the destination. 
def get_file(file_name, file_path):
    config = {'user':os.environ['OS_USERNAME'],
    'key':os.environ['OS_PASSWORD'],
    'tenant_name':os.environ['OS_TENANT_NAME'],
    'authurl':os.environ['OS_AUTH_URL']}

    conn = swiftclient.client.Connection(auth_version=2, **config)

    obj = conn.get_object('matstorage', file_name)
    f = open(file_path, 'w')
    f.write(obj[1])
    f.close()