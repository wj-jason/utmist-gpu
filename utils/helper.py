from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth
from colorama import Fore, Style
import time
import colorama
import argparse

colorama.init()
load_dotenv()

API_KEY = os.getenv('API_KEY')

def query(endpoint: str):
    response = requests.get(
            endpoint,
            auth=HTTPBasicAuth(API_KEY, '')
            )

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("[ERROR] ", response.status_code)
        print(response)
        return False

def get_all_instances():
    endpoint = "https://cloud.lambdalabs.com/api/v1/instances"
    data = query(endpoint)
    
    instances = []
    if data:
        for inst in data['data']:
            instances.append(inst)

    return instances

def print_instance_details():
	instances = get_all_instances()
	if instances:
		for inst in instances:
			name = inst["instance_type"]["name"];
			price  = inst["instance_type"]["price_cents_per_hour"]/100
			inst_id = inst["id"]

			print(f"Instance: {name}\nPrice per hour: {price}\nId: {inst_id}")
			print("----------------------------------------")
	else:
		print("No instances available.")
    
def launch_instance(
        region_name: str = "us-east-1",
        instance_type_name: str = "gpu_1x_a100_sxm4",
        ssh_key_names: list[str] = ["ssh-key-general"],
        file_system_names: list[str] = [],
        quantity: int = 1
        ):
	print("Launching instance...") 
	payload = {
			"region_name": region_name,
			"instance_type_name": instance_type_name,
			"ssh_key_names": ssh_key_names,
			"file_system_names": file_system_names,
			"quantity": 1
			}
	endpoint = "https://cloud.lambdalabs.com/api/v1/instance-operations/launch"
	response = requests.post(
			endpoint,
			auth=HTTPBasicAuth(API_KEY, ''),
			json=payload
			)
	endpoint = "https://cloud.lambdalabs.com/api/v1/instances"
	data = query(endpoint)
	if data:	
		name = data["data"][0]["instance_type"]["name"];
		price  = data["data"][0]["instance_type"]["price_cents_per_hour"]/100
		inst_id = data["data"][0]["id"]

		print(f"Instance: {name}\nPrice per hour: {price}\nId: {inst_id}")


def terminate_instance(instance_id):
	endpoint = "https://cloud.lambdalabs.com/api/v1/instance-operations/terminate"
	data = {"instance_ids": [instance_id]}
	response = requests.post(
			endpoint,
			auth=HTTPBasicAuth(API_KEY, ''),
			json=data
			)
	if response: print(response.json())
	else: print('[ERROR]')

def terminate_all():
    endpoint = "https://cloud.lambdalabs.com/api/v1/instances"
    data = query(endpoint)
    
    if data:
        instance_ids = [inst["id"] for inst in data['data']]
        if instance_ids:
            payload = {"instance_ids": instance_ids}
            terminate_endpoint = "https://cloud.lambdalabs.com/api/v1/instance-operations/terminate"
            response = requests.post(
                terminate_endpoint,
                auth=HTTPBasicAuth(API_KEY, ''),
                json=payload
            )
            
            if response.status_code == 200:
                print("All instances terminated.")
            else:
                print("[ERROR] Failed to initiate termination:", response.status_code)
                print(response.json())
        else:
            print("No instances to terminate.")
    else:
        print("[ERROR] Failed to fetch instances.")

def main():
	parser = argparse.ArgumentParser(description="Lambda Cloud API Client")
	parser.add_argument('--ls', action='store_true', help='Get all instances')
	parser.add_argument('--launch', action='store_true', help='Start an instance')
	parser.add_argument('--stop', type=str, help='Stop an instance by ID')
	parser.add_argument('--prune', action='store_true', help='Stop all instances')

	args = parser.parse_args()

	if args.ls: print_instance_details()
	if args.launch: launch_instance()
	if args.stop: terminate_instance(args.stop)
	if args.prune: terminate_all()

if __name__ == '__main__':
    main()

