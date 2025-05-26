# Repository Summary
## Ansible directory
- Create_VM_with_NGT
   - Ansible playbook to deploy a new VM with NGT with ansible v2 collection
## API
 - ExportVM
   - python script to export VM info. Works with API v3 and v4 (no SDK)
 - BulkCategoryAssignment
   - python script to assign categories to VM in bulk mode
## Calm directory
- LCM_Repo_VM_Darksite
   - Calm BP in json format (Use import BP under Calm, no passphrase)
   - This BP deploy a VM with webserver, and allows to push Nutanix bundle as Day-2 operations. You just have to provide the link.
- RB_Borwnfield_App
   - Calm runbook in json format to create easily brownfield app
## IntelligentOpsPlaybooks directory
- SyncProjects
   - Simple way to synchrone Self-Service VM projects with remote PC