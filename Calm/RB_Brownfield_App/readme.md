# RB_Brownfield_App

## Purpose
This Nutanix Self-Service runbbok is dedicated to create app from (an) existing VM and an existing blueprint. 

This is an automation of this blogpost : [Link](https://www.nutanix.dev/2023/03/31/nutanix-calm-dsl-brownfield-apps-the-easy-way/)

## Prerequisites
All `shell` tasks need to be executed on a jumphost, with Calm DSL installed on it, an preconfigured as admin.

## Details
This runbook supports :
- import of application with multiple VM
    - In this case you need to define list of IP in the good order, with comma as separator
- import of multiple applications
    - In this case, create multiple lines with IP. Each line is a list of IP for imported App
    - All name will be postfixed with `-<number>`