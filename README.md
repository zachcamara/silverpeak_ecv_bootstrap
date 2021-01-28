# Silver Peak Edge Connect EVE-NG Bootsrap
Quickly bootstrap a Silver Peak Virtual Edge Connect assigning a desired Orchestrator, registering with Account/Key, and assigning MAC addresses to interfaces (up to 9 total: mgmt0, wan/lan0-3).

# Requirements
- Leverages silverpeak_python_sdk for API calls to Edge Connect
    - Included subscripts that can be individual called:
        - silverpeak_ec_assign_orch.py -- Function for assigning an Orchestrator and Account to an Edge Connect
        - silverpeak_ec_automap.py -- Function for assigning available MAC addresses to interfaces based on incrementing MAC's

# Methods

1. Assign MAC addresses in ascending order:


    | MAC | ECV Interface |
    | --- | --- |
    | 1 | mgmt0 |
    | 2 | wan0 |
    | 3 | lan0 |
    | 4 | wan1 |
    | 5 | lan1 |
    | 6 | wan2 |
    | 7 | lan2 |
    | 8 | wan3 |
    | 9 | lan3 |
___


2. Assign MAC addresses in ascending order of Network Adapters on ESXi:

    | Network Adapter | ECV Interface |
    | --- | --- |
    | 1 | mgmt0 |
    | 2 | wan0 |
    | 3 | lan0 |
    | 4 | wan1 |
    | 5 | lan1 |
    | 6 | wan2 |
    | 7 | lan2 |
    | 8 | wan3 |
    | 9 | lan3 |
___

# Environment Variables

For incrementing MAC addresses you only require environment variables for Orchestrator and Account information.

```
export ORCH_URL="<ORCH-URL-OR-IP>" 
export ACCOUNT="<ORCH-ACCOUNT-NAME>" 
export ACCOUNT_KEY="<ORCH-ACCOUNT-KEY>" 
```

These are also modeled in dotenv.txt and can be set in a .env file

To assign via Network Adapter in ESXi you must also include environment variables for the ESXi host to connect to.

```
export ESXI_SERVER="<ESXI-URL-OR-IP>" 
export ESXI_USER="<ESXI-USERNAME>" 
export ESXI_PASSWORD="<ESXI-PASSWORD>" 
```


# Syntax

Run the script and then enter each Edge Connect mgmt0 IP address to be bootstrapped. If you chose the ESXi Network Adapter Method you'll also have to provide the associated VM names.

The script will check the following readiness indicators to allow an ECV IP to be added:
- The IP entered is a valid IP address
- The IP can be reached by ping
- Performing a GET request returns a valid expected string URI from the Edge Connect

When entry is complete mark 'n' and then confirm 'y' to proceed with the confirmed IP's.


# Validated Silver Peak Code Versions
- Orchestrator 9.0+
- ECOS 9.0+
- ESXi 6.7

Reporting Issues:
If you have bugs or other issues file them [here](issues).
