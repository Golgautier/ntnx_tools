# LCM_Repo_Darksite

This Blueprint creates an LCM VM with httpd server to provide package to dark site PC.
A day 2 operation is available to update repository, you juste have to give an URL of bundle.tgz. It will be downloaded and extracted on the LCM VM

On PC side, to not forget to specify this VM as LCM target. You need to use URL `http://<LCM VM IP>/release`

After uploading this json under Calm, please :
- Update the credentials (for this VM and for PC connection - for disk extension)
- update VM Image to use (use CentOS or RHEL image)
- update NIC