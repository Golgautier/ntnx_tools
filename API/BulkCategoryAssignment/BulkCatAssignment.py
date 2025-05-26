#!python3

import requests
import json
import csv
import sys
import getpass
import os
import uuid

csvSeparator=","
categoryStartColumn=5 # Column where categories start in the CSV file (0-indexed)

def getCategoriesNames(row):
    """
    Extracts category names from a row of the CSV file.
    Assumes categories start from the 6th column (index 5).
    """
    categories = []
    for i in range(categoryStartColumn, len(row)):
        if row[i].strip():  # Check if the category name is not empty
            categories.append(row[i].strip())
            
    return categories

def getCategoriesUuids(catList):
    """
    Retrieves the UUIDs of categories from Prism Central based on the provided category names.
    """
    page=0
    eltPerPage=50
    allCatFound=False
    
    categoriesUuids = {}
    
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
            responseJson = json.loads(response.text)           

            for cat in responseJson["data"]:
                if cat["key"] in catList:
                    categoriesUuids[cat["key"]+":"+cat["value"]] = cat["extId"]
        else:
            print("Request failed with status code:", response.status_code)
            print("Response text:", response.text)
            return None
        
        if responseJson["metadata"]["totalAvailableResults"] < eltPerPage*(page+1):
            allCatFound = True
            return categoriesUuids
        else:
            page += 1

def updateVM(row, catList, categoriesUuids, pc, pcPort, secureConnection, pcUser, pcPassword, dryRun):
    """
    Executes the category assignment for a given row in the CSV file.
    """
    catForVm = []
    skipVm = False
    warnCat = []
    assignedCat=[]
    
    # Loop through the categories and their values
    for i in range(categoryStartColumn, len(row)):
        if row[i].strip():  # Check if the category value is not empty
            catName = catList[i - categoryStartColumn]
            catValue = row[i].strip()
            catKey = f"{catName}:{catValue}"
            
            if catKey in categoriesUuids:
                catForVm.append(categoriesUuids[catKey])
                assignedCat.append(catKey)
            else:
                warnCat.append(catKey)
                skipVm = True
    
    if not catForVm:
        print(f"  - VM '{row[0]}' : No  categories to assign")
        return
    
    if skipVm:
        print(f"  - VM '{row[0]}' : WARNING. Skipping as it has at least a no valid category assignment : {', '.join(warnCat)}")
        return
    else:
        print(f"  - VM '{row[0]}' : Assigning categories :",assignedCat)
    
    
    if secureConnection == "yes":
        checkSSL = True
    else:
        checkSSL = False
    
    # Get VM info
    url = f"https://{pc}:{pcPort}/api/vmm/v4.0/ahv/config/vms?$filter=(name eq '{row[0].strip()}')"
    
    # Set the headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Set the authentication for the request
    auth = (pcUser, pcPassword)

    response = requests.get(url, headers=headers, auth=auth, verify=checkSSL)
    
    if response.status_code > 299:
        print(f"  - VM '{row[0]}' : WARNING. Skipping because VM is not found or an error occurred {response.status_code}.")
        return
    
    # Parse the JSON response
    responseJson = json.loads(response.text)
    
    # VM Not found
    if not responseJson["data"]:
        print(f"  - VM '{row[0]}' : WARNING. Skipping because VM is not found.")
        return
    
    # Multiple VMs found
    if len(responseJson["data"]) > 1:
        print(f"  - VM '{row[0]}' : WARNING. Skipping because multiple VMs found with the same name.")
        return
    
    # Get the VM UUID
    vmUuid = responseJson["data"][0]["extId"]
    
    # Get VM details
    url = f"https://{pc}:{pcPort}/api/vmm/v4.0/ahv/config/vms/{vmUuid}"
    
    response = requests.get(url, headers=headers, auth=auth, verify=checkSSL)
    
    if response.status_code > 299: 
        print(f"  - VM '{row[0]}' : WARNING. Skipping because an error occurred while getting VM details.")
        return
    
    # Collect the ETag for optimistic concurrency control
    etag = response.headers.get('ETag')
    
    payload = {
        "categories": []  # Initialize the categories list
    }
    
    # We add categories to the payload        
    for catToAdd in catForVm:  
        payload["categories"].append({ 'extId': catToAdd })
    
    url = f"https://{pc}:{pcPort}/api/vmm/v4.0/ahv/config/vms/{vmUuid}/$actions/associate-categories"
    
    # Set the headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'If-Match': etag,  # Use the ETag for optimistic concurrency control
        'Ntnx-Request-Id': str(uuid.uuid4())
    }
    
    if dryRun:
        print(f"    . !! DRY RUN !! Categories used to be assigned here")
    else:
        response = requests.post(url, headers=headers, auth=auth, verify=checkSSL, data=json.dumps(payload))
        if response.status_code < 400:
            print(f"    . Categories assignment launched successfully ({response.status_code})")
        else:
            print(f"    . ERROR: Categories assignment failed with status code: {response.status_code} / {response.text}")
    
    return 
        

# === MAIN ===

# Validate CLI usage
if len(sys.argv) <2:
    print("Usage: python3 BulkCatAssignment.py <CSV_file>")
    print("Example: python3 BulkCatAssignment.py myVM.csv")
    sys.exit(1)

# Check if the provided argument is a CSV file
if sys.argv[1].endswith('.csv'):
    csvFile = sys.argv[1]
else:
    print("Error: The file must be a CSV file.")
    sys.exit(1)
    
if not os.path.isfile(csvFile) or not os.access(csvFile, os.R_OK):
    print(f"Error: The file '{csvFile}' does not exist or is not readable.")
    sys.exit(2)

# Ask user for inputs
pc = input("Enter IP for your Pism Central: ")
pcPort = input("Enter your Prism Central port (default 9440): ")
if pcPort == "":
    pcPort = 9440
secureConnection = input("Use secure connection only (default: yes): ")
if secureConnection == "":
    secureConnection = "yes"
pcUser = input("Enter your Pism Central admin username (default: admin): ")
if pcUser == "":
    pcUser = "admin"
pcPassword = getpass.getpass("Enter your Prism Central admin password: ")

confirm = input("\nIMPORTANT : Have all categories and their values been created in Prism Central? (yes/no): ")
if confirm.strip().lower() != "yes":
    print("Please create all categories and values in Prism Central before running this script.")
    sys.exit(3)

dryRunAnswer = input("\nAre you doing a simple simulation (default: yes): ")
if dryRunAnswer == "":
    dryRunAnswer = "yes"
    
if dryRunAnswer.lower() == "yes":
    print("This is a dry run, no changes will be made to the VMs.\n")
    dryRun=True
else:
    print("This is NOT a dry run, changes will be made to the VMs.\n")
    dryRun=False
   
# We open the CSV file and read its content
with open(csvFile, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=csvSeparator)
    
    # Line counter
    line=1
    
    for row in reader:
        if line==1:
            catList=getCategoriesNames(row)
            categoriesUuids = getCategoriesUuids(catList)            
        else:
            if line == 2:
                print("Assigning categories to VMs...")
                
            updateVM(row, catList, categoriesUuids, pc, pcPort, secureConnection, pcUser, pcPassword,dryRun)
        
        
        # Increment line counter
        line += 1
