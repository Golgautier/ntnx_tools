# AOS_VG_List

## Description ##

This go binary allows to list all VG from a Prism Central, and display, for each of them :
- UUID
- Name
- Storage Container hosting it
- Description

The output is done in a csv file : ./output.csv

## Usage ##

Copy from `binary` folder the binary to use.

You just have to launch the binary, without any parameter. Script will ask for :
- PE FQDN or IP
- PE User
- PE User password

## Compile your own binary ##
If you prefer to create your own binary. Download code from this folder, install golang on you computer, and launch command

`go build -o <binary name> .`