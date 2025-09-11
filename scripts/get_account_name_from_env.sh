#!/usr/bin/env bash

set -euo pipefail

# Validate input arguments
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <environment> <local_directory>" >&2
  exit 1
fi

env="${1}"
localdir="${2}"

# Check if local directory exists
if [ ! -d "$localdir" ]; then
  echo "Error: Directory '$localdir' does not exist." >&2
  exit 1
fi

# Determine tfvars_environment
tfvars_environment=""
if [[ "${env}" =~ ^de- ]]; then
  tfvars_environment="dynamic_environments"
elif [[ "${env}" =~ ^de[0-9]- ]]; then
  tfvars_environment="dynamic_environments${env:2:1}"
else
  tfvars_environment=$env
fi

tfvars_file="${localdir}/etc/env_eu-west-2_${tfvars_environment}.tfvars"

# Check if tfvars file exists
if [ ! -f "$tfvars_file" ]; then
  echo "Error: Terraform variables file '$tfvars_file' not found." >&2
  exit 1
fi

# Extract account name from tfvars file
account_name="$(grep -E '^account_name\s+=' "$tfvars_file" | sed -E "s/account_name\s+=\s+\"(.*)\"/\1/")"

if [ -z "$account_name" ]; then
  echo "Error: Account name not found in '$tfvars_file'." >&2
  exit 1
fi

# Output the account name to stdout
echo "$account_name"
