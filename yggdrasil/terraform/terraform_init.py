import sys
import os
from yggdrasil.common_tools import *

def init(logger, provider, scope, workfolder) :

    logger.info("Init action")

    logger.info("Creating secrets folder")
    secrets_folder = os.path.join(workfolder, 'secrets')
    makedir_p(secrets_folder)

    logger.info("Creating Terraform modules")
    tf_modules_folder = os.path.join(workfolder, 'terraform')
    makedir_p(tf_modules_folder)

    logger.info("Creating scopes folder")
    scopes_folder = os.path.join("scopes", scope)
    makedir_p(scopes_folder)

def apply(logger, provider, scope, workfolder) :

    logger.info("Init action")

def refresh(logger, provider, scope, workfolder) :

    logger.info("Init action")

def destroy(logger, provider, scope, workfolder) :

    logger.info("Init action")



