import os
from dotenv import load_dotenv
import time
import requests
import psutil

load_dotenv()

# Get the API token from the environment variable
api_token = os.getenv('DO_API_TOKEN')

# Set your Droplet tag
droplet_tag = ''

# Set the CPU threshold for scaling
cpu_threshold = 70

# Set your Load Balancer ID
load_balancer_id = ''

# Set the maximum number of instances you want to scale to
max_instances = 4

# Set the minimum number of instances you want to scale to
min_instances = 1

# Function to get CPU usage
def get_cpu_usage():
    return psutil.cpu_percent(interval=300) #the interval shows the number of periods in seconds it will check to make sure that the droplet is within a particular threshold

# Function to list Droplets with a specific tag
def list_droplets_by_tag(tag):
    headers = {'Authorization': f'Bearer {api_token}'}
    params = {'tag_name': tag}
    response = requests.get('https://api.digitalocean.com/v2/droplets', headers=headers, params=params)
    return response.json().get('droplets', [])

# Function to add a Droplet to the Load Balancer
def add_droplet_to_load_balancer(droplet_id):
    headers = {'Authorization': f'Bearer {api_token}', 'Content-Type': 'application/json'}
    data = {'droplets': [droplet_id]}
    response = requests.post(f'https://api.digitalocean.com/v2/load_balancers/{load_balancer_id}/droplets', json=data, headers=headers)
    return response.status_code

# Function to remove a Droplet from the Load Balancer
def remove_droplet_from_load_balancer(droplet_id):
    headers = {'Authorization': f'Bearer {api_token}', 'Content-Type': 'application/json'}
    data = {'droplets': [droplet_id]}
    response = requests.delete(f'https://api.digitalocean.com/v2/load_balancers/{load_balancer_id}/droplets', json=data, headers=headers)
    return response.status_code

# Function to create a snapshot of a Droplet
def create_snapshot(droplet_id):
    headers = {'Authorization': f'Bearer {api_token}', 'Content-Type': 'application/json'}
    snapshot_name = f'dynamic-snapshot-{int(time.time())}'
    data = {'type': 'snapshot', 'name': snapshot_name}
    response = requests.post(f'https://api.digitalocean.com/v2/droplets/{droplet_id}/actions', json=data, headers=headers)
    
    # Check if the snapshot creation request was successful
    if response.status_code == 201:
        snapshot_id = response.json().get('action', {}).get('id')
        print(f"Snapshot creation initiated for Droplet {droplet_id} - Snapshot ID: {snapshot_id}")
    else:
        print(f"Error initiating snapshot creation: {response.text}")

# Function to scale out (create new Droplets)
def scale_out(desired_instances):
    print(f"Scaling out - Creating {desired_instances} new Droplets from Snapshot")
    headers = {'Authorization': f'Bearer {api_token}', 'Content-Type': 'application/json'}

    for _ in range(desired_instances):
        # Replace 'new_droplet_name' with the desired name for the new Droplet you want to 
        new_droplet_name = f'pelstix-{int(time.time())}'

        # Data for creating a new Droplet from a snapshot
        data = {
            'name': new_droplet_name,
            'region': '', #replace with the region of your droplet
            'size': '',  # Replace with the desired size (e.g., 's-1vcpu-1gb')
            'image': snapshot_id,  # Use the snapshot ID for the new Droplet
            'tags': [droplet_tag],
            'ssh_keys': [''],  # Replace with the ID of your SSH key
            'backups': False,
            'ipv6': False,
            'private_networking': None,
            'volumes': None,
            'user_data': generate_user_data_script(),
        }

        # Create the new Droplet
        response = requests.post('https://api.digitalocean.com/v2/droplets', json=data, headers=headers)

        # Check if the new Droplet was created successfully
        if response.status_code == 202:
            droplet_id = response.json().get('droplet', {}).get('id')
            print(f"New Droplet created with ID: {droplet_id}")

            # Add the new Droplet to the Load Balancer
            add_droplet_to_load_balancer(droplet_id)
        else:
            print(f"Error creating Droplet: {response.text}")

# Main loop for monitoring
while True:
    try:
        cpu_usage = get_cpu_usage()
        print(f"Current CPU Usage: {cpu_usage}%")

        # List Droplets with the specified tag
        droplets = list_droplets_by_tag(droplet_tag)
        num_droplets = len(droplets)

        # Calculate the difference between the desired and current number of instances
        instances_diff = max(min_instances, min(max_instances, num_droplets)) - num_droplets

        if cpu_usage > cpu_threshold and instances_diff > 0:
            # Scale out if CPU usage is above the threshold and the desired instances count is greater
            scale_out(instances_diff)
        elif cpu_usage <= cpu_threshold and instances_diff < 0:
            # Scale in if CPU usage is below the threshold and the desired instances count is smaller
            # Choose a Droplet to scale in (you may want to implement a more intelligent selection logic)
            droplet_to_scale_in = droplets[0]
            scale_in(droplet_to_scale_in['id'])

    except Exception as e:
        print(f"Error: {e}")

    # Sleep for a specified interval before checking again (e.g., every 5 minutes)
    time.sleep(300)
