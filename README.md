NHS Notify Release Test
=======================

This repository contains automated tests for the NHS Notify Release 

The tests cover the following scenarios:

* [NHS Notify Release Testing: Mixed Suppliers - Message Batch](https://nhsd-jira.digital.nhs.uk/browse/CCM-6701)
* [NHS Notify Release Testing: Mixed Suppliers - Mesh](https://nhsd-jira.digital.nhs.uk/browse/CCM-6703)
* [NHS Notify Release Testing: ODS Override](https://nhsd-jira.digital.nhs.uk/browse/CCM-6704)
* [NHS Notify Release Testing: Alternative Contact Details](https://nhsd-jira.digital.nhs.uk/browse/CCM-6705)
* [NHS Notify Release Testing: No Communications Scenarios](https://nhsd-jira.digital.nhs.uk/browse/CCM-6707)
* [NHS Notify Release Testing: NHS App Account](https://nhsd-jira.digital.nhs.uk/browse/CCM-6716)
* [NHS Notify Release Testing: PDF Rendering](https://nhsd-jira.digital.nhs.uk/browse/CCM-8399)
* [NHS Notify Release Testing: Parallel send](https://nhsd-jira.digital.nhs.uk/browse/CCM-8406)
* [NHS Notify Release Testing: Anonymous Patients](https://nhsd-jira.digital.nhs.uk/browse/CCM-9442)
* [NHS Notify Release Testing: Filter rules](https://nhsd-jira.digital.nhs.uk/browse/CCM-6022)

Requirements
============
* [poetry](https://github.com/python-poetry/poetry)


Setup
=====
Add test profile to .aws/config
```
[profile test]
sso_start_url = https://d-9c67018f89.awsapps.com/start#
sso_account_id = 736102632839
sso_role_name=CommsMGR-Developer
region = eu-west-2
sso_region = eu-west-2 
output = json
```

Add setacc command to bash profile (.bashrc/.zshrc)
```
setacc() {
  export AWS_PROFILE=$1
};
export PYTHON=$(which python3)
```

Copy example.env to a .env file and populate values

Create a file called `dev-private.key` and populate it with the value of the dev private key

Create a file valled `client_config.json` and populate it with the value of the mesh cli client config file

Export environment variables
```
source .env
```

Create a virtual environment
```
python -m venv .venv
```

Activate virtual environment
```
source .venv/bin/activate
```

Install dependencies
```
poetry install
```

Set environment to test profile
```
setacc test
```

Login to aws
```
aws sso login
```

Run Tests
=========

Run all tests
```
poetry run pytest
````