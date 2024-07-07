from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth
from colorama import Fore, Style
import time
import colorama

colorama.init()
load_dotenv()

API_KEY = os.getenv('API_KEY')


