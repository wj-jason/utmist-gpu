# GPU Cloud

```
# launch new instance
python3 -m utils.helper --launch

# list active instances and details
python3 -m utils.helper --ls

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
3. Get ssh key (ask Rachel)
4. From root of repository, run any of the commands above
5. Once you have an active instance, run `ssh -i ~/.ssh/<KEY> ubuntu@<INSTANCE_IP>

## Notes

The API can be quite slow in spinning up and termininating instances. If you recently launched an instance and try to launch again, the details on the new launch may be identical to your previous instance (it may have the same ID and IP). Do not worry if this happens, there is just a delay in the API. Wait a few minutes, and call `... --ls` and you should see your new instance with unique ID and IP.

When launching an instance, it may take some time for Lambda to associated a floating IP. As such, `... --ls` may return `N/A` for the IP. Waiting a minute or so will resolve this.

Similar stuff for terminating, as long as you get the success message outputted, Lambda will begin terminating the instance. It will continue to show on `... --ls` until complete termination.
