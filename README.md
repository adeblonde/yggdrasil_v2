# Yggdrasil

## Quickstart

### Prerequisites

#### Terraform

Install Terraform by downloading the binary file from their Downloads section [here](https://www.terraform.io/downloads.html)

### Ansible

Install Ansible

### Using Yggdrasil

#### Infra as Code

Init Infra as Code working tree

```bash
ygg infra init --provider <CLOUD_PROVIDER> [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>] [--upgrade]
```

```bash
ygg infra setup [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>] [--upgrade]
```

```bash
ygg infra apply [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

```bash
ygg infra refresh [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

```bash
ygg infra apply [--scope <SCOPE_NAME>] --target <MODULE_NAME> [--workfolder <PATH_TO_WORKFOLDER>]
```

```bash
ygg infra destroy [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

#### Configuration Management - Preparation of environments

```bash
ygg config init [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>] [--upgrade]
```

```bash
ygg config refresh [--scope <SCOPE_NAME>] [--workfolder <PATH_TO_WORKFOLDER>]
```

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