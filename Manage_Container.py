import os
import swiftclient.client

def put_file(file_name, file_path):
    config = {'user':os.environ['OS_USERNAME'],
    'key':os.environ['OS_PASSWORD'],
   	'tenant_name':os.environ['OS_TENANT_NAME'],
   	'authurl':os.environ['OS_AUTH_URL']}

    conn = swiftclient.client.Connection(auth_version=2, **config)

    with open(file_path, 'rb') as f:
        file_data = f.read()
    conn.put_object('matstorage', file_name, file_data)

def get_file(file_name, file_path):
    config = {'user':os.environ['OS_USERNAME'],
    'key':os.environ['OS_PASSWORD'],
    'tenant_name':os.environ['OS_TENANT_NAME'],
    'authurl':os.environ['OS_AUTH_URL']}

    conn = swiftclient.client.Connection(auth_version=2, **config)

    obj = conn.get_object('matstorage', file_name)
    with open(file_path, 'w') as f:
        f.write(obj[1])