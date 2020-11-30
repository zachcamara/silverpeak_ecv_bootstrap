from dotenv import load_dotenv
import colored
from colored import stylize
import getpass
import os
import ipaddress
from ecosHelp import ecosHelper
from silverpeak_ec_automap import ec_auto_map
from silverpeak_ec_assign_orch import ec_assign_orch

# Disable Cert Warnings connecting to new Edge Connect
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def valid_and_reachable(ec_ip):
    # Check if IP address is valid format
    try:
        ipaddress.ip_address(ec_ip)

        # Check if IP address is reachable by ping
        ping_check = os.system("ping -c 1 -W 2 " + ec_ip)

        if ping_check == 0:
            try:
                ec = ecosHelper(ec_ip)
                http_check = ec.ec_api_id
                print("Edge Connect Unique ID: {0}".format(http_check))
                return True
            except:
                print (stylize("{0}: Could not connect to Edge Connect via HTTP, please check again before adding".format(ec_ip),red_text))
                return False

        else:
            print (stylize("{0}: Could not ping Edge Connect, please check again before adding".format(ec_ip),red_text))
            return False

    except ValueError:
        print(stylize("{0} is not a valid IP address to be added".format(ec_ip),red_text))
        return False



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

    if not any(ec['ec_ip'] == ec_ip for ec in ec_ip_list):
        if valid_and_reachable(ec_ip) == True:
            tag = input(stylize("Please enter tag for Edge Connect (e.g. SITE-1, can be left blank): ",blue_text))
            print(stylize("{0}: Edge Connect has been added to list for bootstrap".format(ec_ip),green_text))
            ec_ip_list.append({'ec_ip':ec_ip, 'tag':tag})
        else:
            pass
    else:
        print(stylize("{0} was a duplicate IP that you've already entered".format(ec_ip),red_text))

    check = input(stylize("Do you want to enter more Edge Connects? (y/n): ",orange_text))
    if check == "y" or check == "n":
        enter_more_ec = check
    else:
        pass


if not ec_ip_list:
    print(stylize("No valid Edge Connects were added to bootstrap. Exiting",red_text))
    exit()

else:

    print (stylize("These are the Edge Connects that will be bootstrapped:",blue_text))
    for ec in ec_ip_list:
        print (ec['ec_ip'], " { TAG:", ec['tag'],"}")

    proceed = input(stylize("Proceed? (y/n): ",blue_text))
    if proceed == "y":
        # Assign Orchestrator and Account License to Edge Connect
        for ec in ec_ip_list:
            try:
                print(stylize("\n\nAssigning Orchestrator to {0}".format(ec['ec_ip']),green_text))
                ec_assign_orch(ec['ec_ip'], orchestrator, account, accountKey, tag=ec['tag'])
            except:
                print(stylize("\n\nFailed to assign Orchestrator to Edge Connect at {0}".format(ec['ec_ip']),red_text))

        # Map interfaces to MAC addresses, this will incur a reboot of the Edge Connect
        for ec in ec_ip_list:
            try:
                print(stylize("\n\nMapping Interfaces on {0}".format(ec['ec_ip']),green_text))
                ec_auto_map(ec['ec_ip'])
            except:
                print(stylize("\n\nFailed to auto-map Edge Connect at {0}".format(ec['ec_ip']),red_text))

    else:
        exit()
