#!/usr/bin/python
# Contact: steve@arista.com 
# Purpose: Search for interfaces wth macRxLocalFault = True, and shut them down with user approval.
#          NOTE: There are instances where macRxLocalFault can be True where it isn't really an issue depending
#          on the PHY, but this is generally situations where nothing is connected to the interface.  The change
#          count and time of last change is also included for additional information to help discern if there
#          is anything stale.  
#          NOTE:  The change count timer cannot be cleared.

from jsonrpclib import Server
import ssl
import json
from datetime import datetime, timedelta

##! Below is an example return of 'show interfaces all mac detail' API command for reference:
# {
#   "jsonrpc": "2.0",
#   "id": "EapiExplorer-1",
#   "result": [
#     {
#       "interfaces": {
#         "Ethernet1": {
#           "adminEnabled": true,
#           "phyState": "linkUp",
#           "phyStateChangeCount": 26,
#           "phyStateLastChangeTime": 1764309972.755347,
#           "intfState": "linkUp",
#           "intfStateChangeCount": 28,
#           "intfStateLastChangeTime": 1764309973.3730695,
#           "macRxLocalFault": false,
#           "macRxLocalFaultChangeCount": 0,
#           "macRxLastLocalFaultChangeTime": 0,
#           "macRxRemoteFault": false,
#           "macRxRemoteFaultChangeCount": 0,
#           "macRxLastRemoteFaultChangeTime": 0,
#           "additionalStatus": {}
#         },
#         "Ethernet2": {
#           "adminEnabled": true,
#           "phyState": "linkDown",
#           "phyStateChangeCount": 1,
#           "phyStateLastChangeTime": 1763619720.2167792,
#           "intfState": "linkDown",
#           "intfStateChangeCount": 3,
#           "intfStateLastChangeTime": 1763619748.4503613,
#           "macRxLocalFault": false,
#           "macRxLocalFaultChangeCount": 0,
#           "macRxLastLocalFaultChangeTime": 0,
#           "macRxRemoteFault": false,
#           "macRxRemoteFaultChangeCount": 0,
#           "macRxLastRemoteFaultChangeTime": 0,
#           "additionalStatus": {}
#         },

##! Begin script
try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
	# Legacy Python that doesn’t verify HTTPS certificates by default
	pass
else:
	# Handle target environment that doesn’t support HTTPS verification
	ssl._create_default_https_context = _create_unverified_https_context

#Update the username, password, and device management address
user = "steve"
passwd = "p@ssw0rd"
device_address = "192.168.99.11"

# -------------------------------------------------------------------
# 1. Retrieve detailed interface information
# -------------------------------------------------------------------
switch = Server( f'https://{user}:{passwd}@{device_address}/command-api' )
data = switch.runCmds( 1, ['show interfaces all mac detail'] )
interfaces = data[0]['interfaces']

# -------------------------------------------------------------------
# 2. Collect ALL interfaces with macRxLocalFault = True
# -------------------------------------------------------------------

faulty_interfaces = []

for intf_name, intf_data in interfaces.items():

    mac_fault = intf_data.get("macRxLocalFault", True)
    fault_time = intf_data.get("macRxLastLocalFaultChangeTime")
    change_count = intf_data.get("macRxLocalFaultChangeCount",)

    if mac_fault:
        now = datetime.now()
       	delta = now - datetime.fromtimestamp(fault_time)
       	total_seconds = int(delta.total_seconds())
       	hours = total_seconds // 3600
       	minutes = (total_seconds % 3600) // 60
       	seconds = total_seconds % 60

       	faulty_interfaces.append({
            "name": intf_name,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "count": change_count
        })

# -------------------------------------------------------------------
# 3. Report faulty interfaces
# -------------------------------------------------------------------

if not faulty_interfaces:
    print("\n✅ No interfaces have macRxLocalFault = True. Nothing to shut down.\n")
    exit(0)

print("\n⚠️  The following interfaces have macRxLocalFault = True:\n")

for item in faulty_interfaces:
    print(f"  • {item['name']} — last state change {item['hours']}h "
          f"{item['minutes']}m {item['seconds']}s ago. {item['count']} Changes")

print("\nTotal faulty interfaces:", len(faulty_interfaces))

# -------------------------------------------------------------------
# 4. Ask for approval to shut down ONLY the faulty interfaces
# -------------------------------------------------------------------

approve = input("\nApprove shutdown of ALL listed interfaces? (yes/no): ").strip().lower()

if approve not in ["yes", "y"]:
    print("\nShutdowns canceled. No interfaces were shut down.\n")
    exit(0)

print("\nShutdown approved. Shutting down faulty interfaces...\n")

# -------------------------------------------------------------------
# 5. Shutdown interfaces that have faults
# -------------------------------------------------------------------

for item in faulty_interfaces:
    intf = item["name"]
    print(f"→ Shutting down {intf}...")

    switch.runCmds( 1, ['enable',
    	'configure',
    	f'interface {intf}',
    	'shutdown'
    	])

print("\n✔ All faulty interfaces have been shut down.\n")