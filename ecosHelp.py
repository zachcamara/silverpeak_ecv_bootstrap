import requests
import json
import urllib3

 
class ecosHelper:

    def __init__(self, ipaddress, user="admin", password="admin"):
        self.ipaddress = ipaddress
        self.ec_api_id = requests.Session().get("https://" + ipaddress, timeout=120, verify=False).url.replace("https://" + ipaddress + "/","").replace("/php/user_login.php","")
        self.url_prefix = "https://" + ipaddress + ":443/" + self.ec_api_id + "/rest/json"
        self.session = requests.Session()
        self.data = {}
        self.headers = {}
        self.user = user
        self.password = password
        self.apiSrcId = "?source=menu_rest_apis_id"  #for API calls w/ just source as query param
        self.apiSrcId2 = "&source=menu_rest_apis_id" #for API calls w/ multiple query params
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def login(self):
        try:
            response = self.post("/login", {"user": self.user, "password": self.password})
            if response.status_code == 200:
                print ("{0}: Edge Connect login success".format(self.ipaddress))
                # get and set X-XSRF-TOKEN
                for cookie in response.cookies:
                    if cookie.name == "edgeosCsrfToken":
                        self.headers["X-XSRF-TOKEN"] = cookie.value
                    if cookie.name == "vxoaSessionID":
                        self.headers["vxoaSessionID"] = cookie.value
                return True
            else:
                print ("{0}: Edge Connect login failed: {1}".format(self.ipaddress, response.text))
                return False
        except:
            print("{0}: Exception - unable to connect to Edge Connect".format(self.ipaddress))
            return False

    def logout(self):
        response = self.post("/logout","")
        if response.status_code == 200:
            print("{0}: Edge Connect logout success".format(self.ipaddress))
        else:
            print("{0}: Edge Connect logout failed: {1}".format(self.ipaddress, response.text))

    def get_orchestrator(self):
        # GET operation to retrieve current orchestrator of appliance
        try:
            response = self.get("/gms")
            if response.status_code == 200:
                return response
            else:
                print("Failed to retrieve Orchestrator from Edge Connect at {0}".format(self.ipaddress))
                return False
        except:
            print("{0}: Exception - unable to get Orchestrator from Edge Connect".format(self.ipaddress))
            return False

    def assign_orchestrator(self, orchestrator, ssl_enabled="false", keepalive_count=0, port=0):
        # POST operation to point appliance at Orchestrator
        # As of 9.0.1.0 the self_var as "" appears to fail, and instead not using it returns 200
        response = self.post("/gms", data = {orchestrator : {"self": orchestrator, "ssl_enabled": ssl_enabled, "keepalive_count": keepalive_count, "port": port}})
        if response.status_code == 200:
            return True
        else:
            print("Failed to change appliance {0} to orchestrator {1}".format(self.ipaddress,orchestrator))
            return False


    def register_spPortal_status(self):
        # GET operation to retrieve registration status of appliance
        response = self.get("/spPortal/register")
        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve registration status from Edge Connect at {0}".format(self.ipaddress))
            return False

    def register_spPortal(self, accountKey, account, group="", site=""):
        # POST operation to register Edge Connect with and Account/Key
        response = self.post("/spPortal/register", data = {"accountKey":accountKey, "account":account, "group":group, "site":site})
        if response.status_code == 200:
            return True
        else:
            print("Failed to register appliance {0} to account {1}".format(self.ipaddress,account))
            return False


    def save_changes(self):
        # POST operation to register Edge Connect with and Account/Key
        try:
            response = self.post("/saveChanges","")
            if response.status_code == 200:
                return True
            else:
                print("Failed to save changes to appliance {0}".format(self.ipaddress))
                return False
        except:
            print("{0}: Exception - unable to save changes to Edge Connect due to {1}".format(self.ipaddress,Exception))
            return False

    def is_reboot_required(self):
        # GET operation to check if reboot is required
        response = self.get("/license/isRebootRequired")
        if response.status_code == 200:
            return response
        else:
            print("Failed to check if reboot is required for {0}".format(self.ipaddress))
            return False

    def request_reboot(self,clear_nm="false",delay=0,next_partition="false",reboot_type="Normal", save_db="false", applyBeforeReboot={"hostname":""}):
        # POST operation to perform reboot
        response = self.post("/reboot", data = {"clear_nm":clear_nm, "delay":delay, "next_partition":next_partition, "reboot_type":reboot_type, "save_db":save_db, "applyBeforeReboot":applyBeforeReboot})
        if response.status_code == 200:
            return response
        else:
            print("Failed to request reboot for {0}".format(self.ipaddress))
            return False

    def get_appliance_interfaces(self):
        # GET operation to retrieve interface information
        response = self.get("/interfaces")
        if response.status_code == 200:
            return response
        else:
            print(response.status_code)
            print("Failed to retrieve interface information from {0}".format(self.ipaddress))
            return False

    def get_appliance_network_interfaces(self):
        # GET operation to retrieve interface information
        response = self.get("/networkInterfaces")
        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve network interface information from {0}".format(self.ipaddress))
            return False

    def modify_network_interfaces(self, ifInfo):
        # POST operation to modify network interfaces on Edge Connect
        response = self.post("/networkInterfaces", data = {"ifInfo":ifInfo})
        if response.status_code == 200:
            return True
        else:
            print("Failed to modify network interfaces on appliance {0}".format(self.ipaddress))
            return False
        

    def post(self, url, data):
        #print(self.url_prefix + url)
        return self.session.post(self.url_prefix + url, json=data, verify=False, timeout=120, headers=self.headers)

    def get(self, url):
        return self.session.get(self.url_prefix + url, verify=False, timeout=120, headers=self.headers)

    def delete(self, url):
        return self.session.delete(self.url_prefix + url, verify=False, timeout=120, headers=self.headers)

    def put(self, url, data):
        return self.session.put(self.url_prefix + url, json=data, verify=False, timeout=120, headers=self.headers)

        

