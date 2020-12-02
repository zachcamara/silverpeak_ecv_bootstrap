from dotenv import load_dotenv
import colored
from colored import stylize
import getpass
import os
import requests
import time

# Helper for API interaction with Silver Peak Edge Connect
from ecosHelp import ecosHelper

# Console text highlight color parameters
red_text = colored.fg("red") + colored.attr("bold")
green_text = colored.fg("green") + colored.attr("bold")
blue_text = colored.fg("steel_blue_1b") + colored.attr("bold")
orange_text = colored.fg("dark_orange") + colored.attr("bold")


def ec_assign_orch(ec_ip, orchestrator, account, accountKey, ec_user="admin", ec_pass="admin", tag="",orch_check="n"):
    print(tag)
    ec = ecosHelper(ec_ip, ec_user, ec_pass)

    ec.login()

    # Retrieve current Orchestrator and Account configured on Edge Connect
    print(stylize("########## CHECKING CURRENT STATUS ##########",orange_text))
    try:
        current_orchestrator = ec.get_orchestrator().json()
        print("Current Orchestrator: "+ stylize(current_orchestrator,blue_text))
    except:
        print("Could not retrieve current Orchestrator for {0} due to {1}".format(ec_ip,Exception))
    try:
        current_reg_status = ec.register_spPortal_status().json()
        print("Current Account: " + stylize(current_reg_status['account'],blue_text))
    except:
        print("Could not retrieve current registration information for {0}".format(ec_ip))

    # New Orchestrator and Account to be configured on Edge Connect
    print("The new Orch will be: " + stylize(orchestrator,blue_text))
    print("The new Account will be: " + stylize(account,blue_text))

    # Assign new Orchestrator and Account Details
    print(stylize("########## CONFIGURING ORCH AND ACCOUNT ##########",orange_text))
    try:
        ec.assign_orchestrator(orchestrator)
    except:
        print("Could not assign new Orchestrator {0} to Edge Connect {1}".format(orchestrator,ec_ip))
    try:
        if tag == "":
            ec.register_spPortal(accountKey, account)
        else:
            ec.register_spPortal(accountKey, account, site=tag)
    except:
        print("Could not assign new account {0} to Edge Connect {1}".format(account,ec_ip))
    
    time.sleep(7)

    print(stylize("########## SAVING CHANGES ##########",orange_text))
    ec.save_changes()

    time.sleep(7)


    if orch_check == 'y':
        # Wait for up to 40 seconds for appliance reach new Orchestrator, checking every 10 seconds
        print(stylize("########## WAITING FOR REGISTRATION ##########",orange_text))

        reachable = 'unknown'
        i = 0

        while True:
            i = i + 1
            if (reachable != 'Reachable') and (i < 4):
                try:
                    reachable = ec.get_orchestrator().json()[orchestrator]['webSocket']
                    if reachable != 'Reachable':
                        print("ECV to Orchestrator web socket status: {0}, waiting 10s for next attempt".format(reachable))
                        time.sleep(10)
                except:
                    print("Could not get status from Edge Connect {0} (attempt: {1})".format(ec_ip,i))
            else:
                print("Not registered with Orchestrator after 4 attempts, moving on...")
                break
    else:
        pass
    
    try:
        # Retrieve new status before logging out
        print(stylize("########## CHECKING NEW STATUS ##########",orange_text))
        current_orchestrator = ec.get_orchestrator().json()
        print("Current Orchestrator: "+ stylize(current_orchestrator,blue_text))
        current_reg_status = ec.register_spPortal_status().json()
        print("Current Account: " + stylize(current_reg_status['account'],blue_text))
    except:
        print("Could not retrieve current status from Edge Connect {0} before logging out".format(ec_ip))

    ec.logout()




if __name__ == "__main__":

    # Load environment variables
    load_dotenv()

    # Set Orchestrator and Account Details from .env
    orchestrator = (str(os.getenv('ORCH_URL')))
    account = os.getenv('ACCOUNT')
    accountKey = os.getenv('ACCOUNT_KEY')

    # Set custom Edge Connect Credentials, otherwise defaults to admin/admin
    ec_default_creds = input("Are default credentials in use for the Edge Connect(s)? (y/n): ")

    if ec_default_creds == 'n':
        print(stylize("Enter Edge Connect Credentials:", blue_text))
        ec_user = getpass.getuser()
        ec_pass = getpass.getpass()
    else:
        pass


    # Enter IP address of single Edge Connect
    ec_ip = input("Please enter IP address of Edge Connect to Migrate (e.g. 10.1.30.100): ")

    # Login to Edge Connect
    if ec_default_creds == 'y':
        ec_assign_orch(ec_ip, orchestrator, account, accountKey)
    else:
        ec_assign_orch(ec_ip, orchestrator, account, accountKey, ec_user, ec_pass)