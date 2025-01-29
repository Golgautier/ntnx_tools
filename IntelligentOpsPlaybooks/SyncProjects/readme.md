# Sync Projects

## Purpose
When you use Nutanix Self-Service VM, projects are only considered in this VM. Remote PC will use `_internal` project to store the VM. This tool reasign VMs in the good project.

## Usage

### Prerequisites
- Create a Linux VM that will launch the python script
- On this VM, download the `ChangeProject.py` script and updates IP and credential variables
- Import `UpdateProjectPlaybook.pbk` as a new playbook in `Intelligent Ops` of Prism Central 
- Change IP and credentials of SSH operation and enable the playbook
- As soon as you create a new project on Slef-Service VM, create it on you remote PC too (Can/Should be automated)

### Usage
- As soon as a VM is created, the rebook will be executed, and will try to update the project of you VM to fit with `CalmProject` category

# Limitations
- Won't be applied on cloned VM
- RBAC assigned to Self-Service VM projects are not linked to the PC project. Ensure you configure access in the same way