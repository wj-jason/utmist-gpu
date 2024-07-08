# GPU Cloud

```
# launch new instance
python3 -m utils.helper --launch <SSH_KEY_NAME>

# list active instances and details
python3 -m utils.helper --ls

# list all ssh key names
python3 -m utils.helper --lsk

# stop instance by ID
python3 -m utils.helper --stop <INSTANCE_ID>

# stop all instances
python3 -m utils.helper --prune
```
## To use:
1. Clone this repository
2. Get Lambda API key, place it in `.env` (ask Rachel)
```
# .env
API_KEY =
```
3. Get ssh key (ask Rachel) [help](https://lambdalabs.com/blog/getting-started-with-lambda-cloud-gpu-instances)
4. From root of repository, run any of the commands above
5. Once you have an active instance, run `ssh -i ~/.ssh/<KEY> ubuntu@<INSTANCE_IP>`

## Full Example

After setting everything up, we can start by checking if any instances are active, and the known ssh keys on the account:
```
jason@jason:~/git_repos/utmist-gpu$ python3 -m utils.helper --ls
No instances available.
jason@jason:~/git_repos/utmist-gpu$ python3 -m utils.helper --lsk
['ssh-key-general', 'ssh-key-andrew', 'ssh-key-a100']
```

Next we can launch an instance, specifying the ssh key that is on your machine (see **notes** for why IP is N/A):
```
jason@jason:~/git_repos/utmist-gpu$ python3 -m utils.helper --launch ssh-key-general
Launching instance
Instance launched.
Instance: gpu_1x_a100_sxm4
Price per hour: $1.29
Id: <INSTANCE_ID>
IP: N/A
```

After it completes, we can find the ip address by listing the active instances:
```
jason@jason:~/git_repos/utmist-gpu$ python3 -m utils.helper --ls
---------------------------------------
Instance: gpu_1x_a100_sxm4
Price per hour: $1.29
Id: <INSTANCE_ID>
IP: <INSTANCE_IP>
---------------------------------------
```

Finally we can ssh into our instance using the specified ip address
```
jason@jason:~/git_repos/utmist-gpu$ ssh -i ~/.ssh/ssh-key-general.pem ubuntu@<INSTANCE_IP>

Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 6.2.0-37-generic x86_64)
 .============.
 ||   __      ||    _                    _         _
 ||   \_\     ||   | |    __ _ _ __ ___ | |__   __| | __ _
 ||    \_\    ||   | |   / _` | '_ ` _ \| '_ \ / _` |/ _` |
 ||   /_λ_\   ||   | |__| (_| | | | | | | |_) | (_| | (_| |
 ||  /_/ \_\  ||   |_____\__,_|_| |_| |_|_.__/ \__,_|\__,_|
  .============.                                  GPU CLOUD

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Mon Jul  8 16:50:24 UTC 2024

  System load:  0.62451171875      Processes:                408
  Usage of /:   5.0% of 496.03GB   Users logged in:          0
  Memory usage: 0%                 IPv4 address for docker0: xxx.xx.x.x
  Swap usage:   0%                 IPv4 address for eno1:    xx.xx.xx.xxx


Expanded Security Maintenance for Applications is not enabled.

4 updates can be applied immediately.
4 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable

17 additional security updates can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm


The list of available updates is more than a week old.
To check for new updates run: sudo apt update

ubuntu@<INSTANCE_IP>:~$
```

**Remember to remove your instances after you're done!!!!!!!!**
## Notes

The API can be quite slow in spinning up and termininating instances. If you recently launched an instance and try to launch again, the details on the new launch may be identical to your previous instance (it may have the same ID and IP). Do not worry if this happens, there is just a delay in the API. Wait a few minutes, and call `... --ls` and you should see your new instance with unique ID and IP.

When launching an instance, it may take some time for Lambda to associated a floating IP. As such, `... --ls` may return `N/A` for the IP. Waiting a minute or so will resolve this.

Similar stuff for terminating, as long as you get the success message outputted, Lambda will begin terminating the instance. It will continue to show on `... --ls` until complete termination.
