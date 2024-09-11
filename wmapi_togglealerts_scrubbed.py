import os
import requests
import json
from prettytable import PrettyTable

### Purpose
# Steve King (steve@arista.com)
#
# The purpose of this script is to:
# 1. Log in to the Wireless Manager(WM) API
# 2. Print a list of locations and their associated Location IDs
# 3. Get alert enabled status for <locationid> and prompt user if they want to change
# 4. Toggle alerts on or off for <locationid> and all sub-locations based on input
# 5. Log out of the WM API
#
#
### How to Use
# 1. Update the values for <myapiurl>, <mykey>, and <mykeyvalue>
# 2. Run the script

## Global variables
# Update these with your own values, examples are provided
myapiurl ="https://awm12345-c4.srv.wifi.arista.com/wifi/api"
mykey = "KEY-ATN123456-1234"
mykeyvalue = "abcd1234abcd1234abcd1234abcd1234"

#!! Do not modify these keys:
locationid = ""
seshid = ""
enablealerts = "nochange"

## Function to log into WM API
def wmlogin():
  global seshid

  url = "{}/session".format(myapiurl)
  payload = json.dumps({
    "type": "apikeycredentials",
    "keyId": "{}".format(mykey),
    "keyValue": "{}".format(mykeyvalue),
    "timeout": 3600
  })
  headers = {
  'Content-Type': 'application/json'
  }

  # Login to WM
  print("")
  print("Logging in to WM API...")
  print("")
  response = requests.request("POST", url, headers=headers, data=payload)

  # Return the JSESSIONID for use elsewhere
  seshid = response.headers['set-cookie'].split(";")[0]
  return seshid


## Function to get Location data
def wmget_location():
  global data_location

  url_loc = "{}/locations?pagesize=100".format(myapiurl)
  payload = ""
  headers = {
    'Content-Type': 'application/json',
    'Cookie': seshid
  }

# Convert Location Data to Python Dicts
  locations = requests.request("GET", url_loc, headers=headers, data=payload)
  data_location = json.loads(locations.text)

## Function to print location data in PrettyTable
def wmprint_location():
  global locationid
  wmget_location()

  x = PrettyTable()
  x.field_names = ["ID", "Name"]
  
  t1_name = (data_location['name'])
  t1_id = (data_location['id']['id'])
  x.add_row([(t1_id), t1_name])
  for t2 in data_location['children']:
    if 'id' in data_location:
        t2_name = (t2['name'])
        t2_id = (t2['id']['id'])
        x.add_row([t2_id, t2_name])
        for t3 in t2['children']:
          t3_name = (t3['name'])
          t3_id = (t3['id']['id'])
          x.add_row([t3_id, t3_name])
  
  print("")
  print("Location Mapping:")
  print(x)
  locationid = input("Which LocationID would you like enable or disable alerts for? (LocationID Number): ")
  wmget_alertstatus()

## Function to get alert activation status for <locationid> and prompt to change or not
def wmget_alertstatus():
  global locationid
  global enablealerts
  
  url_alert = "{}/configuration/locationproperty/eventactivation?locationid={}".format(myapiurl,locationid)
  payload = ""
  headers = {
    'Content-Type': 'application/json',
    'Cookie': seshid
  }

  # Convert alert data to Python Dicts
  alertstatus = requests.request("GET", url_alert, headers=headers, data=payload)
  data_alert = json.loads(alertstatus.text)

  # Provide user with alert enablement status for <locationid> and prompt for change, then update
  # <enablealerts> based on input
  if data_alert['eventGenerationActivated'] == True:
    print("Alerts are enabled for LocationID {}".format(locationid))
    user_input = input("Do you want to disable them? (yes/no): ")
    if user_input.lower() in ["yes","y"]:
      # Update required - execute wmput_alertstatus
      enablealerts = "update_disable"
      wmput_alertstatus()
    else:
      enablealerts = "nochange"
      print("No change. Exiting")
  elif data_alert['eventGenerationActivated'] == False:
    print("Alerts are disabled for LocationID {}".format(locationid))
    user_input = input("Do you want to enable them? (yes/no): ")
    if user_input.lower() in ["yes","y"]:
      # Update required - execute wmput_alertstatus
      enablealerts = "update_enable"
      wmput_alertstatus()
    else:
      # No update required - exit
      enablealerts = "nochange"
      print("No change. Exiting")
  else:
    print("DEBUG(wmget_alertstatus):There was an error.")

## Function to update alert enablement status for location
def wmput_alertstatus():
  global locationid
  
  url_alert = "{}/configuration/locationproperty/eventactivation?locationid={}".format(myapiurl,locationid)
  payload_disable = {
    "policyCreatedAtLocId": {
      "type": "locallocationid",
      "id": locationid
    },
    "policyType": "EVENT_ACTIVATION_POLICY",
    "eventGenerationActivated": False,
    "recursiveApply": True
  }
  payload_enable = {
    "policyCreatedAtLocId": {
      "type": "locallocationid",
      "id": locationid
    },
    "policyType": "EVENT_ACTIVATION_POLICY",
    "eventGenerationActivated": True,
    "recursiveApply": True
  }

  headers = {
    'Content-Type': 'application/json',
    'Cookie': seshid
  }

  # Call API and enable or disable alert generation for <locationid> based on <enablealerts>
  if enablealerts == "update_enable":
    response = requests.request("PUT", url_alert, headers=headers, data=json.dumps(payload_enable))
    print("")
    print("Response from WM:")
    print(response.text)
  elif enablealerts == "update_disable":
    response = requests.request("PUT", url_alert, headers=headers, data=json.dumps(payload_disable))
    print("")
    print("Response from WM:")
    print(response.text)
  elif enablealerts == "update_nochange":
    print("")
    print("No change. Exiting.")
  else:
    print("DEBUG(wmput_alertstatus): There was an error.")

## Function to logout of WM API
def wmlogout():
  global seshid

  url = "{}/session".format(myapiurl)
  payload = ""
  headers = {
    'Cookie': seshid
  }

  # Call API
  print("")
  print("Logging Out of WM API...")
  print("")
  response = requests.request("DELETE", url, headers=headers, data=payload)


# Main function
def main():
  wmlogin()
  wmprint_location()
  wmlogout()

#Execute
main()