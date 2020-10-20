#!/bin/bash

for module in $(ls yggdrasil/libraries/terraform/modules)
do
    echo $module
    if [ -d yggdrasil/libraries/terraform/modules/$module ]
    then
        # echo "module folder for module $module exists"
        for terraform_module_file in main.tf variables.tf outputs.tf
        do
            # echo $module/$terraform_module_file
            if [ ! -f yggdrasil/libraries/terraform/modules/$module/$terraform_module_file ]
            then
                echo "module file yggdrasil/libraries/terraform/modules/$module/$terraform_module_file does not exist, creating"
                # touch yggdrasil/libraries/terraform/modules/$module/$terraform_module_file
            else
                echo "module file yggdrasil/libraries/terraform/modules/$module/$terraform_module_file already exists"
            fi
        done
		for cloud_provider in aws azure gcp
		do
			mkdir yggdrasil/libraries/terraform/modules/$module/$cloud_provider
			cp yggdrasil/libraries/terraform/modules/$module/main.tf yggdrasil/libraries/terraform/modules/$module/$cloud_provider/main.tf
		done
    fi
done