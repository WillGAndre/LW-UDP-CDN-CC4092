#!/usr/bin/python3

# Requires: gcloud CLI & Auth

import json
import time
import random
import subprocess

def get_zones() -> list:
    regions_command = [
        "gcloud", "compute", "zones", "list", "--format=json"
    ]
    out = subprocess.check_output(regions_command)
    regions = json.loads(out)
    return [r['name'] for r in regions]

def describe_vm(project_id, zone, instance_name):
    check_command = [
        'gcloud', 'compute', 'instances', 'describe', instance_name,
        '--project', project_id,
        '--zone', zone,
    ]

    # Execute the gcloud command and check the return code
    return subprocess.run(check_command, stdout=subprocess.DEVNULL).returncode == 0

def start_vm(project_id, zone, instance_name):
    start_command = [
        'gcloud', 'compute', 'instances', 'start', instance_name,
        '--project', project_id,
        '--zone', zone,
    ]

    subprocess.run(start_command, check=True)

def create_vm(project_id, zone, instance_name, machine_type, disk_image):
    # Check if the VM already exists
    if describe_vm(project_id, zone, instance_name):
        print(f"VM '{instance_name}' already exists. Starting VM.")
        start_vm(project_id, zone, instance_name)
        time.sleep(15)
        return

    # Construct the gcloud command to create the VM
    create_command = [
        'gcloud', 'compute', 'instances', 'create', instance_name,
        '--project', project_id,
        '--zone', zone,
        '--machine-type', machine_type,
        '--image-project', 'debian-cloud',
        '--image-family', disk_image,
    ]

    # Execute the gcloud command to create the VM
    subprocess.run(create_command, check=True)
    time.sleep(15)

def import_code(project_id, zone, instance_name, local_path, remote_path, recurse=False):
    # Check if the VM already exists
    if not describe_vm(project_id, zone, instance_name):
        print(f"VM '{instance_name}' doesn't exist. Skipping.")
        return

    # Construct the gcloud command to copy the code to the VM
    if not recurse:
        import_command = [
            'gcloud', 'compute', 'scp', local_path,
            f'{instance_name}:/{remote_path}',
            '--project', project_id,
            '--zone', zone,
        ]
    else:
        import_command = [
            'gcloud', 'compute', 'scp', '--recurse', local_path,
            f'{instance_name}:/{remote_path}',
            '--project', project_id,
            '--zone', zone,
        ]

    # Execute the gcloud command to copy the code to the VM
    subprocess.run(import_command, check=True)

def initiate_node_vm(project_id, zone, instance_name, remote_path, command, node_type=0):
    # Check if the VM already exists
    if not describe_vm(project_id, zone, instance_name):
        print(f"VM '{instance_name}' doesn't exists. Skipping.")
        return

    # Construct the gcloud command to initiate the VM with the Python code
    initiate_command = [
        'gcloud', 'compute', 'ssh', instance_name,
        '--project', project_id,
        '--zone', zone,
        '--command', f"""
            sudo apt-get install python3-pip
            pip3 install google-cloud-storage google-auth google-auth-httplib2 google-auth-oauthlib
            python3 /{remote_path}/{command} {zone}
        """        
        # f'python3 /{remote_path}/{command}',
    ]

    # Execute the gcloud command to initiate the VM
    subprocess.run(initiate_command, check=True)

def initiate_lb_vm(project_id, zone, instance_name, remote_path, command):
    # Check if the VM already exists
    if not describe_vm(project_id, zone, instance_name):
        print(f"VM '{instance_name}' doesn't exists. Skipping.")
        return

    # Define the Nginx configuration content
    nginx_config = """
    server {
        listen 80;
        server_name 127.0.0.1;

        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
    }
    """
    nginx_provision = f'sudo apt update && sudo apt install nginx -y && echo "{nginx_config}" | sudo tee /etc/nginx/conf.d/myapp.conf && sudo service nginx restart'
    nginx_command = [
        'gcloud', 'compute', 'ssh', instance_name,
        '--project', project_id,
        '--zone', zone,
        '--command', f"{nginx_provision}"
    ]
    subprocess.run(nginx_command, check=True)

    # Construct the gcloud command to initiate the VM with the Python code
    initiate_command = [
        'gcloud', 'compute', 'ssh', instance_name,
        '--project', project_id,
        '--zone', zone,
        '--command', f"""
            sudo apt update
            sudo apt install nginx
            sudo apt-get install python3-pip
            pip3 install google-cloud-storage google-auth google-auth-httplib2 google-auth-oauthlib flask
            python3 /{remote_path}/{command} {zone}
        """        
        # f'python3 /{remote_path}/{command}',
    ]

    # Execute the gcloud command to initiate the VM
    subprocess.run(initiate_command, check=True)

def __init_ring_node(instance_name='internal-2', zone='us-central1-a'):
    project_id = 'asc23-378811'
    # zone = 'us-central1-a'
    # instance_name = 'internal-2'
    machine_type = 'n1-standard-1'
    disk_image = 'debian-10'
    local_path = 'node/node.py'
    remote_path = 'tmp'
    command = 'node.py'

    # Create the VM
    create_vm(project_id, zone, instance_name, machine_type, disk_image)

    # # Import the code to the VM
    import_code(project_id, zone, instance_name, local_path, remote_path)

    # Initiate the VM with the Python code
    initiate_node_vm(project_id, zone, instance_name, remote_path, command)

def __init_lb():
    project_id = 'asc23-378811'
    zone = 'us-central1-a'
    instance_name = 'lb-1'
    machine_type = 'n1-standard-1'
    disk_image = 'debian-10'
    local_code_path = 'lb/lb.py'
    local_data_sample = 'lb/text3.txt'
    local_templates = 'lb/templates'
    remote_path = 'tmp'
    command = 'lb.py'

    # Create the VM
    create_vm(project_id, zone, instance_name, machine_type, disk_image)

    # # Import the code to the VM
    import_code(project_id, zone, instance_name, local_code_path, remote_path)
    import_code(project_id, zone, instance_name, local_data_sample, remote_path)
    import_code(project_id, zone, instance_name, local_templates, remote_path, recurse=True)

    # Initiate the VM with the Python code
    initiate_lb_vm(project_id, zone, instance_name, remote_path, command)

# __init_ring()
# __init_lb()

# __init_ring_node()
__init_lb()