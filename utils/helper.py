from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth
from colorama import Fore, Style, init
import time
import colorama
import argparse

colorama.init()
load_dotenv()

API_KEY = os.getenv('API_KEY')
INSTANCES = []
SSH_KEYS = []

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

def get_ssh_keys():
    endpoint = 'https://cloud.lambdalabs.com/api/v1/ssh-keys'
    data = query(endpoint)
    if data:
        for key in data['data']:
            SSH_KEYS.append(key['name'])

def get_all_instances():
    endpoint = "https://cloud.lambdalabs.com/api/v1/instances"
    data = query(endpoint)
    
    instances = []
    if data:
        for inst in data['data']:
            instances.append(inst)
    return instances

def _init_instances():
    instances = get_all_instances()
    if instances:
        for inst in instances:
            inst_id = inst["id"]
            INSTANCES.append(inst_id)

def print_instance_details():
    instances = get_all_instances()
    if instances:
        print(f"---------------------------------------")
        for inst in instances:
            name = inst["instance_type"]["name"]
            price  = inst["instance_type"]["price_cents_per_hour"]/100
            inst_id = inst["id"]
            ip = inst.get("ip", "N/A")
            print(f"{Fore.GREEN}Instance: {Fore.RESET}{name}")
            print(f"{Fore.YELLOW}Price per hour: {Fore.RESET}${price:.2f}")
            print(f"{Fore.CYAN}Id: {Fore.RESET}{inst_id}")
            print(f"{Fore.MAGENTA}IP: {Fore.RESET}{ip}")
            print(f"---------------------------------------")
    else:
        print(f"{Fore.RED}No instances available.{Fore.RESET}") 

def launch_instance( 
        ssh_key_name: str,
        region_name: str = "us-east-1",
        instance_type_name: str = "gpu_1x_a100_sxm4",
        # ssh_key_names: list[str] = SSH_KEYS,
        file_system_names: list[str] = [],
        quantity: int = 1,
        ):
    # why make it a list if you can't put multiple values???
    ssh_key_names = [ssh_key_name]
    print(f"{Fore.LIGHTBLUE_EX}Launching instance{Fore.RESET}") 
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
    response = response.json()
    inst_id = response["data"]["instance_ids"][0]
    
    endpoint = f"https://cloud.lambdalabs.com/api/v1/instances/{inst_id}"
    data = query(endpoint)
    # print(data)
    if data:    
        print(f"{Fore.LIGHTGREEN_EX}Instance launched.{Fore.RESET}")
        name = data["data"]["instance_type"]["name"]
        price = data["data"]["instance_type"]["price_cents_per_hour"]/100
        ip = data.get("ip", "N/A")
        
        print(f"{Fore.GREEN}Instance: {Fore.RESET}{name}")
        print(f"{Fore.YELLOW}Price per hour: {Fore.RESET}${price:.2f}")
        print(f"{Fore.CYAN}Id: {Fore.RESET}{inst_id}")
        print(f"{Fore.MAGENTA}IP: {Fore.RESET}{ip}")


def terminate_instance(instance_id):
    endpoint = "https://cloud.lambdalabs.com/api/v1/instance-operations/terminate"
    data = {"instance_ids": [instance_id]}
    response = requests.post(
            endpoint,
            auth=HTTPBasicAuth(API_KEY, ''),
            json=data
            )
    if response: print(f"{Fore.LIGHTGREEN_EX}Instance terminated.{Fore.RESET}")
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
                print(f"{Fore.GREEN}All instances terminated.{Fore.RESET}")
                for inst_id in instance_ids:
                    print(inst_id)
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
    parser.add_argument('--lsk', action='store_true', help='Get all SSH key names')
    parser.add_argument('--launch', type=str, help='Start an instance')
    parser.add_argument('--stop', type=str, help='Stop an instance by ID')
    parser.add_argument('--prune', action='store_true', help='Stop all instances')

    args = parser.parse_args()

    if args.ls: print_instance_details()
    if args.lsk: print(SSH_KEYS)
    if args.launch: launch_instance(args.launch)
    if args.stop: terminate_instance(args.stop)
    if args.prune: terminate_all()

if __name__ == '__main__':
    get_ssh_keys()
    main()

