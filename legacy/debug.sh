#!/bin/bash

source ../../user_setenv.sh

export SCENARIO_NAME="test"

if [ ! -f $WORK_DIR/$SCENARIO_NAME ]
then
	mkdir -p $WORK_DIR/$SCENARIO_NAME
	echo "test test" > $WORK_DIR/$SCENARIO_NAME/test.txt
fi

### set config file
./set_config.sh yggdrasil/test/test_config.yml $WORK_DIR/$SCENARIO_NAME/yggdrasil_config.yml $SCENARIO_NAME

### execute yggdrasil
### recompile and reinstall package
# pip3 install -e .
# ygg --configfile $WORK_DIR/$SCENARIO_NAME/yggdrasil_config.yml --workfolder $WORK_DIR/$SCENARIO_NAME
cd ../yggdrasil
python3 yggdrasil/yggdrasil.py "$WORK_DIR/$SCENARIO_NAME/yggdrasil_config.yml" "$WORK_DIR/$SCENARIO_NAME"
