import sys
import os
import shutil
from distutils.dir_util import copy_tree
import json
from yggdrasil.common_tools import *

def init(logger, provider, scope, workfolder, data_path, upgrade=False) :

    logger.info("Init action")

    logger.info("Creating secrets folder")
    secrets_folder = os.path.join(workfolder, 'secrets')
    makedir_p(secrets_folder)

    logger.info("Creating Terraform modules")
    tf_modules_folder = os.path.join(workfolder, 'terraform')
    makedir_p(tf_modules_folder)

    """ we walk through the list of Terraform modules in the package's libraries and copy them """
    libraries_tf_folder = os.path.join(data_path, 'libraries', 'terraform', 'modules')
    # for root, dirs, files in os.walk(libraries_tf_folder) :
    for module_name in os.listdir(libraries_tf_folder) :
        """ dealing with common Terraform modules """
        module_dir = os.path.join(libraries_tf_folder, module_name)
        makedir_p(os.path.join(tf_modules_folder, module_name))

        if provider in os.listdir(module_dir) :
            """ copying main.tf and outputs.tf """
            for tf_file in ['main.tf', 'outputs.tf'] :
                source_file = os.path.join(module_dir, provider, tf_file)
                dest_file = os.path.join(tf_modules_folder, module_name, tf_file)
                if os.path.isfile(source_file) :
                    shutil.copyfile()
                else :
                    logger.info("Error : file %s missing in package source", source_file)
                    
            """ copying variables.tf (common for all providers) """
            source_file = os.path.join(module_dir, 'variables.tf')
            dest_file = os.path(tf_modules_folder, module_name, 'variables.tf')
            if os.path.isfile(source_file) :
                shutil.copyfile()
            else :
                logger.info("Error : file %s missing in package source", source_file)
        
    logger.info("Creating scopes folder")
    source_scopes_folder = os.path.join(data_path, 'libraries', 'terraform', 'scopes')
    copy_tree(source_scopes_folder, workfolder)

    logger.info("Storing info in .ygg file")
    ygg_state = os.path.join(workfolder, '.ygg')
    if os.path.isfile(ygg_state) :
        ygg_data = dict()
        with open(ygg_state, 'w') as f :
            ygg_data = json.load(f)
            ygg_data['provider'] = provider
    else :
        ygg_data = {'provider':provider}

    with open(ygg_state, 'r') as f :
            json.dump(ygg_data, f)
        
    return

def apply(logger, provider, scope, workfolder) :

    logger.info("Init action")

def refresh(logger, provider, scope, workfolder) :

    logger.info("Init action")

def destroy(logger, provider, scope, workfolder) :

    logger.info("Init action")

def output(logger, provider, scope, workfolder):

    logger.info("Output action")
