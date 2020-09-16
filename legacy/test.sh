#!/bin/bash

### set the variables in the configuration file
ygg-config ../yggdrasil/test/test_config.yml -o ~/yggdrasil_test_config.yml
# ygg-config ../yggdrasil/test/test_config.yml -f yggdrasil_params_template.json -o ~/yggdrasil_test_config.yml
# ygg-config ../yggdrasil/test/test_config.yml -v AUTH_DIR="AUTH_DIR" -o ~/yggdrasil_test_config.yml

### run yggdrasil
ygg ~/yggdrasil_test_config.yml --workfolder ~/yggdrasil_test