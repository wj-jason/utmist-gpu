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
SSH_KEYS = []

def print_error(response: dict):
    for key, value in response.items():
        if isinstance(value, dict):
            print(f"{Fore.LIGHTRED_EX}{key}:{Fore.RESET}")
            for sub_key, sub_value in value.items():
                print(f"  {Fore.LIGHTRED_EX}{sub_key}: {sub_value}{Fore.RESET}")
        else:
            print(f"{Fore.LIGHTRED_EX}{key}: {value}{Fore.RESET}")

def query(endpoint: str):
    response = requests.get(
            endpoint,
            auth=HTTPBasicAuth(API_KEY, '')
            )

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print_error(response.json())
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

def print_instance_details():
    instances = get_all_instances()
    if instances:
        print(f"---------------------------------------")
        for inst in instances:
            alias = inst.get("name", "None")
            status = inst["status"]
            name = inst["instance_type"]["name"]
            price = inst["instance_type"]["price_cents_per_hour"]/100
            # price = round(price/100, 2) if price else "N/A"
            inst_id = inst["id"]
            ip = inst.get("ip", "N/A")
            j_url = inst.get("jupyter_url", "N/A")
            print(f"{Fore.CYAN}Alias: {Fore.RESET}{alias}")
            print(f"{Fore.GREEN}Instance: {Fore.RESET}{name}")
            print(f"{Fore.YELLOW}Price per hour: {Fore.RESET}${price:.2f}")
            print(f"{Fore.RED}Status: {Fore.RESET}{status}")
            print(f"{Fore.CYAN}Id: {Fore.RESET}{inst_id}")
            print(f"{Fore.MAGENTA}IP: {Fore.RESET}{ip}")
            print(f"{Fore.BLUE}Jupyter URL: {Fore.RESET}{j_url}") 
            print(f"---------------------------------------")
    else:
        print(f"{Fore.RED}No instances available.{Fore.RESET}") 

def launch_instance( 
        ssh_key_name: str,
        alias: str,
        instance_type_name: str = "gpu_1x_a100_sxm4",
        region_name: str = "us-west-2",
        # ssh_key_names: list[str] = SSH_KEYS,
        file_system_names: list[str] = ["shared-dir"],
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
            "quantity": quantity,
            "name": alias
            }
    endpoint = "https://cloud.lambdalabs.com/api/v1/instance-operations/launch"
    response = requests.post(
            endpoint,
            auth=HTTPBasicAuth(API_KEY, ''),
            json=payload
            )
    if response.status_code != 200:
        print_error(response.json())
        return

    response = response.json()
    inst_id = response["data"]["instance_ids"][0]
    
    endpoint = f"https://cloud.lambdalabs.com/api/v1/instances/{inst_id}"
    data = query(endpoint)
    # print(data)
    if data:    
        print(f"{Fore.LIGHTGREEN_EX}Instance launched.{Fore.RESET}")
        alias = alias if alias else "None"
        name = data["data"]["instance_type"]["name"]
        price = data["data"]["instance_type"]["price_cents_per_hour"]/100
        ip = data.get("ip", "N/A")
        j_url = data.get("jupyter_url", "N/A") 
        print(f"{Fore.CYAN}Alias: {Fore.RESET}{alias}")
        print(f"{Fore.GREEN}Instance: {Fore.RESET}{name}")
        print(f"{Fore.YELLOW}Price per hour: {Fore.RESET}${price:.2f}")
        print(f"{Fore.CYAN}Id: {Fore.RESET}{inst_id}")
        print(f"{Fore.MAGENTA}IP: {Fore.RESET}{ip}")
        print(f"{Fore.BLUE}Jupyter URL:{Fore.RESET} {j_url}")


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

def print_gpus(gpus):
    print(f"{Fore.LIGHTCYAN_EX}NAME: PRICE PER HOUR{Fore.RESET}")
    for (gpu, price) in gpus.items():
        print(f"{gpu}: ${price}")

    print(f"{Fore.LIGHTCYAN_EX}For up-to-date information, see: https://lambdalabs.com/service/gpu-cloud{Fore.RESET}")

def main():
    get_ssh_keys()
    gpus = {
        "gpu_1x_a10": 0.75,
        "gpu_1x_a100_sxm4": 1.29,
        "gpu_8x_h100_sxm5": 27.92,
        "gpu_1x_h100_pcie": 2.49,
        "gpu_8x_a100_80gb_sxm4": 14.32,
        "gpu_1x_rtx6000": 0.5,
        "gpu_1x_a100": 1.29,
        "gpu_2x_a100": 2.58,
        "gpu_4x_a100": 5.16,
        "gpu_8x_a100": 10.32,
        "gpu_1x_a6000": 0.80,
        "gpu_2x_a6000": 1.60,
        "gpu_4x_a6000": 3.20,
        "gpu_8x_v100": 4.40,
    }

    parser = argparse.ArgumentParser(description="Lambda Cloud API Client")
    parser.add_argument('--ls', action='store_true', help='Get all instances')
    parser.add_argument('--gpu', action='store_true', help='See all gpu instances')
    parser.add_argument('--lsk', action='store_true', help='Get all SSH key names')
    parser.add_argument('--launch', type=str, nargs='+', help='Start an instance')
    parser.add_argument('--stop', type=str, help='Stop an instance by ID')
    parser.add_argument('--prune', action='store_true', help='Stop all instances')

    args = parser.parse_args()

    if args.ls: print_instance_details()
    if args.gpu: print_gpus(gpus)
    if args.lsk: print(SSH_KEYS)
    if args.launch: 
        if len(args.launch) not in [2, 3]:
            print(f'''{Fore.LIGHTRED_EX}Usage: fog --launch <KEY_NAME> <ALIAS> <GPU>
    <KEY_NAME>   Your SSH key (Mandatory)
    <ALIAS>      Instance alias (Mandatory)
    <GPU>        GPU instance type (Optional, default='1x_a100_sxm4')
    Run `fog --gpu` for more information on GPU types''')
        else:
            launch_instance(*args.launch)
    if args.stop: terminate_instance(args.stop)
    if args.prune: terminate_all()

if __name__ == '__main__':
    get_ssh_keys()
    main()

