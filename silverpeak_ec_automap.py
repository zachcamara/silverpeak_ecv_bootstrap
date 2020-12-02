import colored
from colored import stylize
import getpass
import time
from tqdm import tqdm

# Helper for API interaction with Silver Peak Edge Connect
from ecosHelp import ecosHelper

# Console text highlight color parameters
red_text = colored.fg("red") + colored.attr("bold")
green_text = colored.fg("green") + colored.attr("bold")
blue_text = colored.fg("steel_blue_1b") + colored.attr("bold")
orange_text = colored.fg("dark_orange") + colored.attr("bold")


def ec_auto_map(ec_ip, ec_user="admin", ec_pass="admin"):

    ec = ecosHelper(ec_ip, ec_user, ec_pass)

    ec.login()

    # Get appliance interfaces, which includes available unnassigned MAC addresses
    interfaces = ec.get_appliance_interfaces().json()

    # Sort out just the relevant availableMacs list
    for item in interfaces:
        try:
            availableMacs = item['dynamic']['availableMacs']
        except:
            pass

    # List of interfaces to modify
    ifInfo = []

    # Map iterating MAC addresses to Edge Connect ports
    for mac in availableMacs:
        if mac[-5:] == "00:00":
            ifInfo.append({'ifname':'mgmt0','mac':mac})
        elif mac[-5:] == "00:01":
            ifInfo.append({'ifname':'wan0','mac':mac})
        elif mac[-5:] == "00:02":
            ifInfo.append({'ifname':'lan0','mac':mac})
        elif mac[-5:] == "00:03":
            ifInfo.append({'ifname':'wan1','mac':mac})
        elif mac[-5:] == "00:04":
            ifInfo.append({'ifname':'lan1','mac':mac})
        elif mac[-5:] == "00:05":
            ifInfo.append({'ifname':'wan2','mac':mac})
        elif mac[-5:] == "00:06":
            ifInfo.append({'ifname':'lan2','mac':mac})
        elif mac[-5:] == "00:07":
            ifInfo.append({'ifname':'wan3','mac':mac})
        elif mac[-5:] == "00:08":
            ifInfo.append({'ifname':'lan3','mac':mac})
        else:
            print ("MAC {0} did not match an expected value to map to an interface")

    if not ifInfo:
        print("There were no available MAC addressess to map to interfaces")
    else:
        print ("The following interface assignments are going to be made:")
        for interface in ifInfo:
            print (stylize(interface['ifname'] + ":  " + interface['mac'],blue_text))

    try:
        ec.modify_network_interfaces(ifInfo)
        # Per API documentation, waiting 30 seconds before another API call after performing a POST to /networkInterfaces
        print(stylize("\n########## INTERFACES MAPPED - PAUSING FOR NEXT API CALL ##########",orange_text))
        
        i = 0
        for i in tqdm(range(10)):
            time.sleep(3)
            i = i + 1

    except:
        print("Unable to assign MAC addresses!")

    # Save changes on Edge Connect
    print(stylize("\n########## SAVING CHANGES ##########",orange_text))
    ec.save_changes()

    # Reboot Edge Connect if required
    print(stylize("\n########## CHECKING FOR REBOOT STATUS ##########",orange_text))
    reboot_required = ec.is_reboot_required().json()
    if reboot_required['isRebootRequired'] == True:
        print(stylize("\n########## CONFIG COMPLETED - REBOOTING APPLIANCE ##########",green_text))
        ec.request_reboot(applyBeforeReboot={"hostname":"eve-silverpeak"})
    else:
        print("No reboot required")
        ec.logout()




if __name__ == "__main__":

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

    # Auto-map interfaces to MAC addresses on Edge Connect
    if ec_default_creds == 'y':
        ec_auto_map(ec_ip)
    else:
        ec_auto_map(ec_ip, ec_user, ec_pass)

