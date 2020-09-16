#!/bin/bash

for module in $(ls yggdrasil/lib/terraform)
do
    echo $module
    if [ -d yggdrasil/lib/terraform/$module ]
    then
        # echo "module folder for module $module exists"
        for terraform_module_file in main.tf variables.tf outputs.tf
        do
            # echo $module/$terraform_module_file
            if [ ! -f yggdrasil/lib/terraform/$module/$terraform_module_file ]
            then
                echo "module file yggdrasil/lib/terraform/$module/$terraform_module_file does not exist, creating"
                touch yggdrasil/lib/terraform/$module/$terraform_module_file
            else
                echo "module file yggdrasil/lib/terraform/$module/$terraform_module_file already exists"
            fi
        done
    fi
done