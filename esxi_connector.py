import pyVim
import pyVmomi
from pyVim import connect
from pyVmomi import vim, vmodl
from vmwc import VMWareClient


class EsxiHelper:
    def __init__(self, ipaddress):
        self.host = ipaddress
        self.user = "root"
        self.password = "password"

    def get_network_int(self, vm_name_string):

        with VMWareClient(self.host, self.user, self.password) as client:
            for vm in client.get_virtual_machines():
                if vm_name_string in vm.name:
                    interfaces = {}
                    for (
                        hardware_device
                    ) in vm._raw_virtual_machine.config.hardware.device:
                        if isinstance(
                            hardware_device, vim.vm.device.VirtualEthernetCard
                        ):
                            interfaces[hardware_device.deviceInfo.label] = {
                                "port_group": hardware_device.deviceInfo.summary,
                                "mac": hardware_device.macAddress,
                            }

                    return interfaces
