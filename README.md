# Yggdrasil

## Quickstart

### Prerequisites

#### Terraform

Install Terraform by downloading the binary file from their Downloads section [here](https://www.terraform.io/downloads.html)

### Ansible

Install Ansible following the instruction [here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

## Using Yggdrasil

### Infra as Code

Init Infra as Code working tree : this command will create a working folder for Terraform in the specified PATH_TO_WORKFOLDER. The workfolder will be created if it does not exist.

You can have several 'scopes' in your working folder, each scope being a separate Terraform project with associated folder tree.

```bash
ygg infra init --provider <CLOUD_PROVIDER> --credentials <PATH_TO_CLOUD_PROVIDER_CREDENTIALS> [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>] [--upgrade] [--region <REGION>] [--blueprint <ARCHITECTURE_BLUEPRINT>]
```

Setup Infra as Code working tree : target a well-formatted Terraform folder tree generated by `ygg infra init` in order to retrieve all the SSH key names, and generate them if they do not exist in the dedicated credential folder. 

You can also provide the path to a local Keepass database file and the dedicated password, in order to retrieve the required SSH keys directly from it.

```bash
ygg infra setup [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>] [--upgrade] [--keepass <PATH_TO_KEEPASS>] [--keepass-password <KEEPASS_PASSWORD>] [--keepass-password-file <PATH_TO_KEEPASS_PASSWORD_FILE>]
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