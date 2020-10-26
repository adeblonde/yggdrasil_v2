#!/bin/bash

### install local requirements
pip3 install -r requirements.txt

### direct debug without rebuild
# infra init
python3 debug.py infra init gcp dev ../../../run/dev "/mnt/c/Users/Antoine/Documents/BT/dev/code/Terraform_Ecosystem/cloud_deployment/credentials/brennus/gcp/dev-deployment-293117-69ab99e1461b.json" us-west1 X

# infra apply
python3 debug.py infra apply gcp dev ../../../run/dev X X X
