# Lambda Cloud for UTMIST (Fog)
For a quick start tutorial: https://www.youtube.com/watch?v=eqP13xZ0_c0
```
# launch new instance (GPU_TYPE is optional, gpu_1x_a100_sxm4 by default)
fog --launch <SSH_KEY_NAME> <ALIAS> <GPU_TYPE>

# list active instances and details
fog --ls

# list all ssh key names
fog --lsk

# list all gpu instances
fog --gpu

# stop instance by ID
fog --stop <INSTANCE_ID>

# stop all instances
fog --prune
```
1. [To Use](#to-use)
2. [Complete Walkthrough](#complete-walkthrough)
3. [Resnet50 Example](#resnet50-example)

## To Use:
1. Clone this repository
2. Create a venv `python3 -m venv venv` and activate it
3. Run `pip install .`
4. Get Lambda API key, place it in `.env` (ask Rachel)
```
# .env
API_KEY =
```
3. Get ssh key (ask Rachel) [help](https://lambdalabs.com/blog/getting-started-with-lambda-cloud-gpu-instances)
4. From root of repository, run any of the commands above
5. Once you have an active instance, run `ssh -i ~/.ssh/<KEY> ubuntu@<INSTANCE_IP>`

**IMPORTANT:** To stay up to date on any changes, ensure to `git pull` and `pip install .` to check for any updates before using.

## Complete Walkthrough

After setting everything up, we can start by checking if any instances are active, and the known ssh keys on the account:
```
(venv) jason@jason:~/git_repos/utmist-gpu$ fog --ls
No instances available.
(venv) jason@jason:~/git_repos/utmist-gpu$ fog --lsk
['ssh-key-general', 'ssh-key-andrew', 'ssh-key-a100']
```

Next we can launch an instance, specifying your SSH key and an alias for the instance (it is recommended that you alias with your name for clarity) . Note that while booting, the IP and Jupyter URL will be unvailable.
```
(venv) jason@jason:~/git_repos/utmist-gpu$ fog --launch ssh-key-general jason
Launching instance
Instance launched.
Alias: jason
Instance: gpu_1x_a100_sxm4
Price per hour: $1.29
Id: <INSTANCE_ID>
IP: N/A
Jupyter URL: N/A
```

Alternatively, we can specify a different GPU instance. To observe all available instances [more information](https://lambdalabs.com/service/gpu-cloud):

```
(venv) jason@jason:~/git_repos/utmist-gpu$ fog --gpu
NAME: PRICE PER HOUR
gpu_1x_a10: $0.75
gpu_1x_a100_sxm4: $1.29
gpu_8x_h100_sxm5: $27.92
gpu_1x_h100_pcie: $2.49
gpu_8x_a100_80gb_sxm4: $14.32
gpu_1x_rtx6000: $0.5
gpu_1x_a100: $1.29
gpu_2x_a100: $2.58
gpu_4x_a100: $5.16
gpu_8x_a100: $10.32
gpu_1x_a6000: $0.8
gpu_2x_a6000: $1.6
gpu_4x_a6000: $3.2
gpu_8x_v100: $4.4
```

For now, (and in general) we will use the default A100 instance. We can check boot progress and other active instances with `ls`
```
(venv) jason@jason:~/git_repos/utmist-gpu$ fog --ls
---------------------------------------
Alias: jason
Instance: gpu_1x_a100_sxm4
Price per hour: $1.29
Status: booting
Id: <INSTANCE_ID>
IP: N/A
Jupyter URL: N/A
```

After a few minutes, we can check again:
```
(venv) jason@jason:~/git_repos/utmist-gpu$ fog --ls
---------------------------------------
Alias: jason
Instance: gpu_1x_a100_sxm4
Price per hour: $1.29
Status: active
Id: <INSTANCE_ID>
IP: <INSTANCE_IP>
Jupyter URL: <JUPYTER_URL>
```

To access the instance, we can SSH using the specified ip address.
```
(venv) jason@jason:~/git_repos/utmist-gpu$ ssh -i ~/.ssh/ssh-key-general.pem ubuntu@<INSTANCE_IP>
```
Or you can access the instance via Juptyer by following the URL.

From the instance, we can view our persistent filesystem.
```
ubuntu@<INSTANCE_IP>:~$ ls
shared-dir
ubuntu@<INSTANCE_IP>:~$ ls shared-dir/
'2024-04-30 raw dataset - tagged only.zip'   annotations_armanm.db   annotations_davidg.db   annotations_sylarl.db
 annotations_alexanderc.db                   annotations_chrisk.db   annotations_sam.db
```

It is up to you how you want to load your models from here, but what I recommend is to access the instance with a Jupyter interface and upload your files locally from there, then either use the Jupyter terminal or SSH into the instance to interact with the uploaded files using the terminal. 

Remember not to touch `shared-dir/` since it contains our dataset which must be shared between instances.

Once you are done with the instance, you can either `prune` all instances, or `stop` a specified instance. Be careful using `prune` as you may delete instance that are not yours. Note that you must delete by referencing the instance ID, not the alias.
```
(venv) jason@jason:~/git_repos/utmist-gpu$ fog --stop <INSTANCE_ID>
Instance terminated.
```

Once terminated, it will stay visible until fully deleted but the status will change to `terminating`. 
```
(venv) jason@jason:~/git_repos/utmist-gpu$ fog --ls
---------------------------------------
Alias: jason
Instance: gpu_1x_a100_sxm4
Price per hour: $1.29
Status: terminating
Id: <INSTANCE_ID>
IP: <INSTANCE_IP>
Jupyter URL: <JUPTYER_URL>
---------------------------------------
```

## Resnet50 Example
To try out the Resnet50 example, follow the above steps to spin up an instance. Copy the 3 `.py` files from `examples/resnet50/` to the instance, then `pip install librosa` and run `main.py`. You should be able to observe data being extracted into the instances temprorary filesystem (everything except `shared-dir/`), and a train/test session using Resnet50 on our dataset.

Note thet all Lambda instances come with the [Lambda Stack](https://lambdalabs.com/lambda-stack-deep-learning-software) pre-installed. This is why we only need to install librosa. 
