from dotenv import load_dotenv
import colored
from colored import stylize
import getpass
import os
from silverpeak_ec_automap import ec_auto_map
from silverpeak_ec_assign_orch import ec_assign_orch

# Disable Cert Warnings connecting to new Edge Connect
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Console text highlight color parameters
red_text = colored.fg("red") + colored.attr("bold")
green_text = colored.fg("green") + colored.attr("bold")
blue_text = colored.fg("steel_blue_1b") + colored.attr("bold")
orange_text = colored.fg("dark_orange") + colored.attr("bold")

# Load environment variables
load_dotenv()

# Set Orchestrator and Account Details from .env
orchestrator = (str(os.getenv('ORCH_URL')))
account = os.getenv('ACCOUNT')
accountKey = os.getenv('ACCOUNT_KEY')

ec_ip_list = []

# Enter IP address of single Edge Connect
enter_more_ec = "y"
while enter_more_ec == "y":
    ec_ip = input(stylize("Please enter IP of Edge Connect (e.g. 10.1.30.100): ",blue_text))
    ec_ip_list.append(ec_ip)
    enter_more_ec = input(stylize("Do you want to enter more Edge Connects? (y/n): ",orange_text))

print (stylize("These are the Edge Connects that will be bootstrapped:",blue_text))
for ec_ip in ec_ip_list:
    print (ec_ip)

proceed = input(stylize("Proceed? (y/n): ",blue_text))
if proceed == "y":
    # Assign Orchestrator and Account License to Edge Connect
    for ec_ip in ec_ip_list:
        try:
            print("Assigning Orchestrator to {0}".format(ec_ip))
            ec_assign_orch(ec_ip, orchestrator, account, accountKey)
        except:
            print(stylize("Failed to assign Orchestrator to Edge Connect at {0}".format(ec_ip),red_text))

    # Map interfaces to MAC addresses, this will incur a reboot of the Edge Connect
    for ec_ip in ec_ip_list:
        try:
            print("Mapping Interfaces on {0}".format(ec_ip))
            eve_ec_auto_map(ec_ip)
        except:
            print(stylize("Failed to auto-map Edge Connect at {0}".format(ec_ip),red_text))

else:
    exit()
