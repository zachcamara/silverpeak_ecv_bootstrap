import getpass
import os
import time

import colored
from colored import stylize
from dotenv import load_dotenv
from silverpeak_python_sdk import EdgeConnect
from tqdm import tqdm

from esxi_connector import EsxiHelper

# Console text highlight color parameters
red_text = colored.fg("red") + colored.attr("bold")
green_text = colored.fg("green") + colored.attr("bold")
blue_text = colored.fg("steel_blue_1b") + colored.attr("bold")
orange_text = colored.fg("dark_orange") + colored.attr("bold")


def ec_increment_available_mac(ec):

    # Get appliance interfaces, which includes available unnassigned MAC addresses
    interfaces = ec.get_appliance_interfaces()

    # Sort out just the relevant availableMacs list
    for item in interfaces:
        try:
            availableMacs = item["dynamic"]["availableMacs"]
        except:
            pass

    # dictionary to store original MAC / converted integer pairings
    mac_dict = {}
    # list to easily sort converted integers of MAC addresses
    mac_int_list = []
    # convert MAC addresses to integers and store pair in dictionary, and store integer in list for sorting
    for mac in availableMacs:
        # replace ":" in MAC so that it's a base-16 hexadecimal number and convert it to an integer
        mac_int = int(mac.replace(":", ""), 16)
        # store in a dictionary as a key for the original MAC address string as its value
        mac_dict[mac_int] = mac
        # add the integer to a list for sorting in ascending order
        mac_int_list.append(mac_int)

    # sort the integer values in ascending order
    mac_int_list.sort()

    # logical ECV interface list
    ecv_interface_names = [
        "mgmt0",
        "wan0",
        "lan0",
        "wan1",
        "lan1",
        "wan2",
        "lan2",
        "wan3",
        "lan3",
    ]

    # List of interfaces to modify
    ifInfo = []

    # Pair available MAC addresses to logical interface names
    i = 0
    while i < len(availableMacs):
        ifInfo.append(
            {"ifname": ecv_interface_names[i], "mac": mac_dict[mac_int_list[i]]}
        )
        i = i + 1

    if not ifInfo:
        print("There were no available MAC addressess to map to interfaces")
    else:
        print("The following interface assignments are going to be made:")
        for interface in ifInfo:
            print(stylize(interface["ifname"] + ":  " + interface["mac"], blue_text))

    return ifInfo


def ec_assign_esxi_adapter_mac(vm_name: str):

    # Load environment variables
    load_dotenv()

    # Set ESXi connection details from .env
    esxi = EsxiHelper(str(os.getenv("ESXI_SERVER")))
    esxi.user = os.getenv("ESXI_USER")
    esxi.password = os.getenv("ESXI_PASSWORD")

    # Get Network Adapter information from VM
    vm_interfaces = esxi.get_network_int(vm_name_string=vm_name)

    # Interfaces are returned in following nested dictionary format:
    # {"Network adapter 1" : {"port_group" : "PORTGROUP NAME", "mac" : "MAC ADDRESS"}}

    ifInfo = []
    if vm_interfaces.get("Network adapter 1") is not None:
        ifInfo.append(
            {"ifname": "mgmt0", "mac": vm_interfaces["Network adapter 1"]["mac"]}
        )
    if vm_interfaces.get("Network adapter 2") is not None:
        ifInfo.append(
            {"ifname": "wan0", "mac": vm_interfaces["Network adapter 2"]["mac"]}
        )
    if vm_interfaces.get("Network adapter 3") is not None:
        ifInfo.append(
            {"ifname": "lan0", "mac": vm_interfaces["Network adapter 3"]["mac"]}
        )
    if vm_interfaces.get("Network adapter 4") is not None:
        ifInfo.append(
            {"ifname": "wan1", "mac": vm_interfaces["Network adapter 4"]["mac"]}
        )
    if vm_interfaces.get("Network adapter 5") is not None:
        ifInfo.append(
            {"ifname": "lan1", "mac": vm_interfaces["Network adapter 5"]["mac"]}
        )
    if vm_interfaces.get("Network adapter 6") is not None:
        ifInfo.append(
            {"ifname": "wan2", "mac": vm_interfaces["Network adapter 6"]["mac"]}
        )
    if vm_interfaces.get("Network adapter 7") is not None:
        ifInfo.append(
            {"ifname": "lan2", "mac": vm_interfaces["Network adapter 7"]["mac"]}
        )
    if vm_interfaces.get("Network adapter 8") is not None:
        ifInfo.append(
            {"ifname": "wan3", "mac": vm_interfaces["Network adapter 8"]["mac"]}
        )
    if vm_interfaces.get("Network adapter 9") is not None:
        ifInfo.append(
            {"ifname": "lan3", "mac": vm_interfaces["Network adapter 9"]["mac"]}
        )

    if not ifInfo:
        print("There were no available MAC addressess to map to interfaces")
    else:
        print("The following interface assignments are going to be made:")
        for interface in ifInfo:
            print(stylize(interface["ifname"] + ":  " + interface["mac"], blue_text))

    return ifInfo


def ec_assign_interfaces(ec, ifInfo: list):
    try:
        ec.modify_network_interfaces(ifInfo)
        # Per API documentation, waiting 30 seconds before another API call after performing a POST to /networkInterfaces
        print(
            stylize(
                "\n########## INTERFACES MAPPED - PAUSING FOR NEXT API CALL ##########",
                orange_text,
            )
        )

        i = 0
        for i in tqdm(range(10)):
            time.sleep(3)
            i = i + 1

    except:
        print("Unable to assign MAC addresses!")

    # Save changes on Edge Connect
    print(stylize("\n########## SAVING CHANGES ##########", orange_text))
    ec.save_changes()

    # Reboot Edge Connect if required
    print(stylize("\n########## CHECKING FOR REBOOT STATUS ##########", orange_text))
    reboot_required = ec.is_reboot_required()
    if reboot_required["isRebootRequired"] == True:
        print(
            stylize(
                "\n########## CONFIG COMPLETED - REBOOTING APPLIANCE ##########",
                green_text,
            )
        )
        ec.request_reboot(applyBeforeReboot={"hostname": "eve-silverpeak"})
    else:
        print("No reboot required")


def ec_interface_map(ec_ip: str, vm_name: str = None):

    ec = EdgeConnect(ec_ip)
    ec.login(user="admin", password="admin")

    # Auto-map interfaces to MAC addresses on Edge Connect
    if vm_name is None:
        ifInfo = ec_increment_available_mac(ec)
        ec_assign_interfaces(ec, ifInfo)
    else:
        ifInfo = ec_assign_esxi_adapter_mac(vm_name)
        ec_assign_interfaces(ec, ifInfo)

    ec.logout()


if __name__ == "__main__":

    # Assume default credentials configured on Edge Connect (admin/admin)

    # Enter IP address of single Edge Connect
    ec_ip = input(
        "Please enter IP address of Edge Connect to map interfaces (e.g. 10.1.30.100): "
    )

    method = input(
        """"Please choose method of MAC address assignments:

        1. Assign interfaces based on ascending order of MAC addresses
        2. Assign interfaces based on ascending order of Network Adapters in ESXi
        
        """
    )

    ec = EdgeConnect(ec_ip)
    ec.login(user="admin", password="admin")

    # Auto-map interfaces to MAC addresses on Edge Connect
    if method == "1":
        ifInfo = ec_increment_available_mac(ec)
        ec_assign_interfaces(ec, ifInfo)
    elif method == "2":
        vm_name = input("Please enter VM name of ECV: ")
        ifInfo = ec_assign_esxi_adapter_mac(vm_name)
        ec_assign_interfaces(ec, ifInfo)
    else:
        print("No valid method chosen")

    ec.logout()
