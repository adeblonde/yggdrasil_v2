# Yggdrasil

## Quickstart

### Prerequisites

#### Python 3

Yggdrasil needs python 3 and pip for python 3 to run

On ubuntu, you can install pip by running 

```bash
sudo apt install python3-pip
```

#### Terraform

Install Terraform by downloading the binary file from their Downloads section [here](https://www.terraform.io/downloads.html)

### Ansible

Install Ansible following the instruction [here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

## Installing Yggdrasil

You can install the Yggdrasil CLI simply by running

```bash
git clone https://github.com/adeblonde/yggdrasil_v2.git
cd yggdrasil_v2
pip3 install -e .
```

## Using Yggdrasil

### Obtaining Cloud Credentials

First, you need to download credentials for a public cloud provider

#### GCP

In order to prepare Terraform for GCP use, you will need to follow the tutorial [here](https://cloud.google.com/community/tutorials/getting-started-on-gcp-with-terraform) until the 'Getting project credentials' section included.

At the end of this section, you will be able to download a json file containing project credentials to access the GCP APIs remotely with Terraform

### AWS

In order to prepare Terraform for AWS use, you will need to get Programmatic Access credentials, following the tutorial [here](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)

You will obtain a .csv file containing your programmatic access credentials

### Azure

In order to prepare Terraform for Azure use, you will need to follow the tutorial [here]](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/terraform-install-configure)

Set the subscription ID for Azure CLI

```bash
az account show --query "{subscriptionId:id, tenantId:tenantId}"
export SUBSCRIPTION_ID=$(az account show --query "{subscriptionId:id, tenantId:tenantId}" | grep subscriptionId | cut -d '"' -f 4)
```

```bash
az account set --subscription="${SUBSCRIPTION_ID}"
az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/${SUBSCRIPTION_ID}"
```

### Quickstart

Once you have cloud credentials, you can execute Yggdrasil like this

```bash
ygg infra init --provider <CLOUD_PROVIDER> --credentials <PATH_TO_CLOUD_PROVIDER_CREDENTIALS>
```

where `<CLOUD_PROVIDER>` should be `aws`, `azure` or `gcp`, and `<CLOUD_PROVIDER>` the path to your cloud credentials file (with the file included).

This command will initialize a 'workfolder' (by default `./yggdrasil`) with the following folder tree :

```txt
yggdrasil
├── scopes
│   └── dev			-> folder containing a complete Terraform setup for deploying a dev architecture
├── secrets			-> folder containing SSH keys for the architecture
└── terraform		-> folder containing Terraform modules used by scopes/dev
```

Then the following command will run Terraform on your "scope" to create it on your chosen cloud account :

```bash
ygg infra apply
```

After creation, dump the data about your architecture, that will be gathered into a new folder `inventories/dev`

```bash
ygg infra output
```

At this step, you will have the following folder tree :

```txt
yggdrasil
├── scopes
│   └── dev
├── secrets
├── inventories
│   └── dev
│       └── terraform_output.json
└── terraform
```

You can then run 

```bash
ygg config init
```

this command will parse `inventories/dev/terraform_output.json` and create the following files :

```txt
yggdrasil
├── scopes
│   └── dev
│── secrets
├── inventories
│   └── dev
│       │── ansible.cfg				-> ansible configuration file
│       │── ssh.cfg					-> ssh configuration file for proxying ansible
│       │── envt.hosts				-> host file for ansible
│       │── paas.ini				-> file gathering information about PaaS cloud services
│       └── terraform_output.jso	
└── terraform
```

You can then move to the `inventories/dev` folder to run ansible playbooks :

```bash
cd inventories/dev
ansible-playbook -i envt.host <PATH_TO_YOUR_ANSIBLE_PLAYBOOKS>
```

Further development of Yggdrasil will include a wrapper on Ansible and a collection of Ansible roles and playbooks in order to allow easy chaining of configuration with deployment.

### Infra as Code

Init Infra as Code working tree : this command will create a working folder for Terraform in the specified PATH_TO_WORKFOLDER. The workfolder will be created if it does not exist.

You can have several 'scopes' in your working folder, each scope being a separate Terraform project with associated folder tree.

```bash
ygg infra init \
--provider <CLOUD_PROVIDER> \
--credentials <PATH_TO_CLOUD_PROVIDER_CREDENTIALS> \
[--scope <SCOPE_NAME>] \
[--workfolder <PATH_TO_WORKFOLDER>] \
[--upgrade] \
[--region <REGION>] \
[--blueprint <ARCHITECTURE_BLUEPRINT>] \
[--tf-library-path <TERRAFORM_LIBRARY_PATH>] \
[--tf-library-name <DESTINATION_NAME_OF_TF_LIBRARY>]
```

Setup Infra as Code working tree : target a well-formatted Terraform folder tree generated by `ygg infra init` in order to retrieve all the SSH key names, and generate them if they do not exist in the dedicated credential folder. 

You can also provide the path to a local Keepass database file and the dedicated password, in order to retrieve the required SSH keys directly from it.

```bash
ygg infra setup \
[--scope <SCOPE_NAME>] \
[--workfolder <PATH_TO_WORKFOLDER>] \
[--upgrade] [--keepass <PATH_TO_KEEPASS>] \
[--keepass-password <KEEPASS_PASSWORD>] \
[--keepass-password-file <PATH_TO_KEEPASS_PASSWORD_FILE>]
```

Once you have a Terraform folder tree with all needed credentials and SSH keys, you can make a `terrafom apply` on your scope with this command.

```bash
ygg infra apply [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

You can also target a specific module with this command :

```bash
ygg infra apply [--scope <SCOPE_NAME>] --target <MODULE_NAME> [--workfolder <PATH_TO_WORKFOLDER>]
```

Once you have a Terraform folder tree with all needed credentials and SSH keys, you can make a `terrafom refresh` on your scope with this command.

```bash
ygg infra refresh [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

After the deployment, you can make a `terrafom refresh` to get the data about your architecture (in order to follow with Ansible configuration, for example).

```bash
ygg infra output [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

Finally, you can destroy a Terraform project with this command.

```bash
ygg infra destroy [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

#### Configuration Management - Preparation of environments

Init Configuration Management : this command will collect the output of Terraform and parse it to extract the SSH configuration and host files needed by Ansible.

```bash
ygg config init [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>] [--upgrade]
```

Refresh Configuration Management : this command will refresh the output of Terraform and re-parse it to update the SSH configuration and host files needed by Ansible.

```bash
ygg config refresh [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

Apply Configuration Management : this command will execute sequentially all playbooks listed in `configuration_management.sh`. If you provide the `--continue` option, the command will get the last point of failure in the last execution from the log file, and restart execution of Ansible's playbooks from this point.

```bash
ygg config apply [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>] [--continue]
```

#### Configuration Management - Execution of workflows

```bash
ygg workflow init [--scope <SCOPE_NAME>] [--target <WORKFLOW_NAME>] [--workfolder <PATH_TO_WORKFOLDER>] [--upgrade]
```

```bash
ygg workflow apply [--scope <SCOPE_NAME>] [--target <WORKFLOW_NAME> [--workfolder <PATH_TO_WORKFOLDER>]
```

```bash
ygg workflow start [--scope <SCOPE_NAME>] [--target <WORKFLOW_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

```bash
ygg workflow stop [--scope <SCOPE_NAME>] [--target <WORKFLOW_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

## Backlog

Secrets management :

- reading a well-formatted Keepass .dbx file on local file system to retrieve and store secrets

GCP :

- implementation of service API activation through [Terraform](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project_service)