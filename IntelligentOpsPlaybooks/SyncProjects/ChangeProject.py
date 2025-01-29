#!/usr/bin/python

from requests import request
import sys
from sys import argv
from jsonpath_ng import jsonpath, parse
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pcIp="<Prism Central IP>"
pcUser="<Prism Central User>"
pcPwd="<Prism Central Password>"

# Small timer to let the VM be created
time.sleep(30)

if len(argv) != 2:
    print("Usage: %s <vmUuid>" % argv[0])
    sys.exit(1)

# Get VM UUID from command line
vmUuid = argv[1]

print("VM UUID: %s" % vmUuid)

# Get CalmProject Value for the VM
url="https://%s:9440/api/nutanix/v3/vms/%s" % (pcIp, vmUuid)

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

try:
    response = request("GET", url, headers=headers, auth=(pcUser, pcPwd), verify=False)
except Exception as e:
    print("Error: %s" % e)
    sys.exit(1)
    
#We handle the answer to get project assigned to it
vmLoad = response.json()

if "CalmProject" in vmLoad['metadata']['categories'].keys():
    targetProject = vmLoad['metadata']['categories']['CalmProject']
else:
    print("This VM does not have CalmProject category")
    sys.exit(2)
    
print("CalmProject: %s" % targetProject)

# Retrieving Project UUID
url="https://%s:9440/api/nutanix/v3/projects/list" % pcIp

payload={
    "kind":"project",
    "length":1,
    "offset":0,
    "filter": "name==%s" % targetProject
}

try:
    response = request("POST", url, json=payload, headers=headers, auth=(pcUser, pcPwd), verify=False)
except Exception as e:
    print("Error: %s" % e)
    sys.exit(1)
    
jsonResponse = response.json()

if len(jsonResponse['entities']) == 0:
    print("Project %s not found" % targetProject)
    sys.exit(3)

projectUuid = jsonResponse['entities'][0]['metadata']['uuid']
print("Project  '%s' UUID is %s" % (targetProject, projectUuid))

# Now we change the VM project
del(vmLoad['status'])

# We change project
vmLoad['metadata']['project_reference'] = {
    'kind': 'project',
    'name': targetProject,
    'uuid': projectUuid
    }

# We now update the vm
url="https://%s:9440/api/nutanix/v3/vms/%s" % (pcIp, vmUuid)

try:
    print("Changing project to %s..." % targetProject)
    response = request("PUT", url, json=vmLoad, headers=headers, auth=(pcUser, pcPwd), verify=False)
except Exception as e:
    print("Error modifying the VM project: %s" % e)
    sys.exit(1)

print("Launched", response.status_code)



