#!python3

import requests
import json
import csv
import sys

csvSeparator=","
internalSeparator=";"

def getList(pc, pcPort, pcUser, pcPassword, secureConnection, apiVersion):
    page=0
    vmPerPage=50
    loopOnVM=True
    returnValue=[]

    if secureConnection == "yes":
        checkSSL = True
    else:
        checkSSL = False
    
    # Set the URL for the API endpoint
    if apiVersion == "4":
        url = f"https://{pc}:{pcPort}/api/vmm/v4.0/ahv/config/vms"
        method = "GET"
        payload={}
    else:
        url = f"https://{pc}:{pcPort}/api/nutanix/v3/vms/list"
        method = "POST"
        payload={
            "kind": "vm",
            }

    # Set the headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Set the authentication for the request
    auth = (pcUser, pcPassword)

    print("Getting VM list...")

    while loopOnVM:
        print("  . Handling page: ", page+1)

        # Update the payload for pagination
        if apiVersion == "3":
            payload["offset"] = page * vmPerPage
            payload["length"] = vmPerPage
        
        # Make the request to the API
        if apiVersion == "4":
            response = requests.get(url+"?$page="+str(page)+"&$limit="+str(vmPerPage), headers=headers, auth=auth, verify=checkSSL)
        elif apiVersion == "3":
            response = requests.post(url, headers=headers, auth=auth, data=json.dumps(payload), verify=checkSSL)
        else:
            print("Invalid API version specified.")
            return None

        # Check if the request was successful
        if response.status_code < 400:
            
            # Parse the JSON response
            vmList = json.loads(response.text)           
            
            # Get totalNumber info
            if apiVersion == "4":
                if "data" in vmList:
                    returnValue.extend(vmList["data"])
                totalVmNumber = vmList["metadata"]["totalAvailableResults"]
            else:
                if "entities" in vmList:
                    returnValue.extend(vmList["entities"])
                totalVmNumber = vmList["metadata"]["total_matches"]
            
            # Check if there are more VMs to fetch
            if totalVmNumber < vmPerPage*(page+1):
                loopOnVM = False
            else:
                # Increment the page number for the next request
                page += 1
        else:
            print("Request failed with status code:", response.status_code)
            print("Response text:", response.text)
            loopOnVM = False
            return None

    return returnValue

def getVmRow_v3(vm):
    # Ourput row will be a list
    # "Name", "UUID", "owner", "Cluster", "Project", "Power State", "IP Addresses", "Categories","vCPUs", "vCores per vCPU", "Memory (GB)", "Disks", "NICS", "NGT Installed", "NGT Version", "Guest OS", "boot type", "vtpm"
    row=[]
    
    # Get the VM properties
    row.append(vm["status"]["name"])
    row.append(vm["metadata"]["uuid"])
    row.append(vm["spec"]["clsuter_reference"]["name"])
    row.append(vm["metadata"]["owner_reference"]["name"])
    row.append(vm["metadata"]["project_reference"]["name"])
    row.append(vm["status"]["resources"]["power_state"])
    
    # Get the IP addresses
    ipAddresses = []
    for nic in vm["status"]["resources"]["nic_list"]:
        if "ip_endpoint_list" in nic:
            for ip in nic["ip_endpoint_list"]:
                ipAddresses.append(ip["ip"])
    row.append(internalSeparator.join(ipAddresses))
    
    # Get the categories
    categories = []
    for key,value in vm["metadata"]["categories"].items():
        categories.append(key + ": " + value)
    row.append(internalSeparator.join(categories))
    
    # Get the vCPUs and Memory
    row.append(vm["spec"]["resources"]["num_sockets"])
    row.append(vm["spec"]["resources"]["num_threads_per_core"])
    row.append(vm["spec"]["resources"]["memory_size_mib"] / 1024)
    
    # Get the disks and NICS
    disks = len(vm["status"]["resources"]["disk_list"])
    nics = len(vm["status"]["resources"]["nic_list"])
    
    row.append(disks)
    row.append(nics)
    
    # Check if NGT is installed
    if "guest_tools" in vm['status']['resources']:
        row.append("Yes")
        
        # Version
        row.append(vm["status"]["resources"]["guest_tools"]["nutanix_guest_tools"]["version"])
        
        # Guest OS
        row.append(vm["status"]["resources"]["guest_tools"]["nutanix_guest_tools"]["guest_os_version"])
    else:
        row.append("No")
        row.append("N/A")
        row.append("N/A")
    
    # Get the  boot type
    row.append(vm["status"]["resources"]["boot_config"]["boot_type"])
    
    # Check if vTPM is enabled
    if vm["spec"]["resources"]["vtpm_config"]["vtpm_enabled"]:
        row.append("Yes")
    else:
        row.append("No")
    
    return row

def getVmRow_v4(vm,clusterList,categoriesList,usersList):
        # Ourput row will be a list
    # "Name", "UUID", "Cluster", "owner", "Project", "Power State", "IP Addresses", "Categories","vCPUs", "vCores per vCPU", "Memory (GB)", "Disks", "NICS", "NGT Installed", "NGT Version", "Guest OS", "boot type", "vtpm"
    row=[]
    
    # Get the VM properties
    row.append(vm["name"])
    row.append(vm["extId"])
    row.append(clusterList[vm["cluster"]["extId"]]) 
    row.append(usersList[vm["ownershipInfo"]["owner"]["extId"]])
    row.append('N/A') #TODO
    row.append(vm["powerState"])
    
    # Get the IP addresses
    ipAddresses = []
    for nic in vm["nics"]:
        if "networkInfo" in nic:
            if "ipv4Config" in nic["networkInfo"]:
                if "ipAddress" in nic["networkInfo"]["ipv4Config"]:
                        ipAddresses.append(nic["networkInfo"]["ipv4Config"]["ipAddress"]["value"])
                        
    # Join all the ipAdresses                        
    row.append(internalSeparator.join(ipAddresses))
    
    # Get the categories
    categories = []
    if 'categories' in vm:
        for cat in vm["categories"]:
            categories.append(categoriesList[cat["extId"]])

    
    # Join all the cat
    row.append(internalSeparator.join(categories))
    
    # Get the vCPUs and Memory
    row.append(vm["numSockets"])
    row.append(vm["numCoresPerSocket"])
    row.append(vm["memorySizeBytes"] / 1024 / 1024)
    
    # Get the disks and NICS
    disks = len(vm["disks"])
    nics = len(vm["nics"])
    
    row.append(disks)
    row.append(nics)
    
    # Check if NGT is installed
    if "guestTools" in vm:
        row.append("Yes")
        
        # Version
        row.append(vm["guestTools"]["version"])
        
        # Guest OS
        row.append(vm["guestTools"]["guestOsVersion"])
    else:
        row.append("No")
        row.append("N/A")
        row.append("N/A")
    
    # Get the  boot type
    if vm["bootConfig"]["$objectType"] == "vmm.v4.ahv.config.LegacyBoot":
        row.append("Legacy")
    elif vm["bootConfig"]["$objectType"] == "vmm.v4.ahv.config.UefiBoot":
        row.append("UEFI")
    else:
        row.append("Unknown")
    
    # Check if vTPM is enabled
    if "vtpmConfig" in vm:
        if vm["vtpmConfig"]["isVtpmEnabled"]:
            row.append("Yes")
        else:
            row.append("No")
    
    return row

def exportVmList(vmList, outputFile, apiVersion, clustersList,categoriesList,usersList):
    # Open the CSV file for writing
    
    with open(outputFile, mode='w', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile,delimiter=csvSeparator)

        # Write the header row
        writer.writerow(["Name", "UUID", "Cluster", "owner", "Project", "Power State", "IP Addresses", "Categories","vCPUs", "vCores per vCPU", "Memory (GB)", "Disks", "NICS", "NGT Installed", "NGT Version", "Guest OS", "boot type", "vtpm"])

        # Write the VM data to the CSV file
        for vm in vmList:
            
            row=[]
            
            if apiVersion == "4":
                row=getVmRow_v4(vm,clustersList,categoriesList,usersList)
            else:
                row=getVmRow_v3(vm)
        
            writer.writerow(row)
    
    print(f"VM list exported to {outputFile}")
    
def getClusterList(pc, pcPort, pcUser, pcPassword, secureConnection):
    
    returnValue={}
    
    print("Getting cluster list...")
    if secureConnection == "yes":
        checkSSL = True
    else:
        checkSSL = False
    
    url = f"https://{pc}:{pcPort}/api/clustermgmt/v4.0/config/clusters"
    
    # Set the headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Set the authentication for the request
    auth = (pcUser, pcPassword)

    
    response = requests.get(url, headers=headers, auth=auth, verify=checkSSL)
    if response.status_code < 400:
        # Parse the JSON response
        clusterList = json.loads(response.text)           

        for cluster in clusterList["data"]:
            returnValue[cluster["extId"]] = cluster["name"]
            
        return returnValue
    else:
        print("Request failed with status code:", response.status_code)
        print("Response text:", response.text)
        return None

def getCategoriesList(pc, pcPort, pcUser, pcPassword, secureConnection):
    page=0
    eltPerPage=50
    allCatFound=False
    
    returnValue={}
    
    print("Getting categories list...")
    if secureConnection == "yes":
        checkSSL = True
    else:
        checkSSL = False
    
    url = f"https://{pc}:{pcPort}/api/prism/v4.0/config/categories"
    
    # Set the headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Set the authentication for the request
    auth = (pcUser, pcPassword)

    while not allCatFound:
        print("  . Handling page: ", page+1)
        
        response = requests.get(url+"?$page="+str(page)+"&$limit="+str(eltPerPage), headers=headers, auth=auth, verify=checkSSL)
        if response.status_code < 400:
            # Parse the JSON response
            catList = json.loads(response.text)           

            for cat in catList["data"]:
                returnValue[cat["extId"]] = cat["key"]+":"+cat["value"]
                
        else:
            print("Request failed with status code:", response.status_code)
            print("Response text:", response.text)
            return None
        
        if catList["metadata"]["totalAvailableResults"] < eltPerPage*(page+1):
            allCatFound = True
            return returnValue
        else:
            page += 1
        
def getUsersList(pc, pcPort, pcUser, pcPassword, secureConnection):
    page=0
    eltPerPage=50
    allUsersFound=False
    
    returnValue={}
    
    print("Getting users list...")
    if secureConnection == "yes":
        checkSSL = True
    else:
        checkSSL = False
    
    url = f"https://{pc}:{pcPort}/api/iam/v4.0/authn/users"
    
    # Set the headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Set the authentication for the request
    auth = (pcUser, pcPassword)

    while not allUsersFound:
        print("  . Handling page: ", page+1)
        
        response = requests.get(url+"?$page="+str(page)+"&$limit="+str(eltPerPage), headers=headers, auth=auth, verify=checkSSL)
        if response.status_code < 400:
            # Parse the JSON response
            catList = json.loads(response.text)           

            for cat in catList["data"]:
                returnValue[cat["extId"]] = cat["username"]
                
        else:
            print("Request failed with status code:", response.status_code)
            print("Response text:", response.text)
            return None
        
        if catList["metadata"]["totalAvailableResults"] < eltPerPage*(page+1):
            allUsersFound = True
            return returnValue
        else:
            page += 1        


# === MAIN ===
apiVersion="4" # Default API version
clustersList={}
categoriesList={}
usersList={}

for args in sys.argv:
    if args == "-v3":
        apiVersion = "3"
    elif args == "-v4":
        apiVersion = "4"
    elif args == "-h":
        print("Usage: python ExportVM.py [-v3|-v4] [-h]")
        print("-v3: Use API version 3")
        print("-v4: Use API version 4 (default)")
        print("-h: Show this help message")
        sys.exit(0)

pc = input("Enter IP for your Pism Central: ")
pcPort = input("Enter your Pism Central port (default 9440): ")
if pcPort == "":
    pcPort = 9440
pcUser = input("Enter your Pism Central admin username (default: admin): ")
if pcUser == "":
    pcUser = "admin"
secureConnection = input("Use secure connection only (default: yes): ")
if secureConnection == "":
    secureConnection = "yes"
pcPassword = input("Enter your Prism Central admin password: ")
outputFile = input("Enter the output file name (default vm_list.csv): ")
if outputFile == "":
    outputFile = "vm_list.csv"

if apiVersion == "4":
    # Get the cluster list
    clustersList=getClusterList(pc, pcPort, pcUser, pcPassword, secureConnection)
    categoriesList=getCategoriesList(pc, pcPort, pcUser, pcPassword, secureConnection)
    usersList=getUsersList(pc, pcPort, pcUser, pcPassword, secureConnection)

# Main part
vmList=getList(pc, pcPort, pcUser, pcPassword, secureConnection, apiVersion)
exportVmList(vmList, outputFile, apiVersion,clustersList,categoriesList,usersList)