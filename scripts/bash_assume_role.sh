#!/usr/bin/env bash

###
# NOTE: _SOURCE_ this file in order to switch to the COMMSAppDeployer role in the correct account
###

set -uo pipefail

# Validate input arguments
env="${1:-}"
localdir="${2:-}"

if [[ -z "${env}" ]]; then
  echo "Error: Environment (env) is not provided." >&2
  exit 1
fi

if [[ -z "${localdir}" || ! -d "${localdir}" ]]; then
  echo "Error: Local directory (localdir) is not provided or is invalid." >&2
  exit 1
fi

# Get account name from tfvars file
account_name="$( source "${localdir}/get_account_name_from_env.sh" "${env}" "${localdir}" 2>/dev/null )"
if [[ -z "${account_name}" ]]; then
  echo "Error: Failed to retrieve account name for environment '${env}'." >&2
  exit 1
fi

# Get account number from account name
account_number="$( source "${localdir}/get_account_number_from_name.sh" "${account_name}" 2>/dev/null )"
if [[ -z "${account_number}" ]]; then
  echo "Error: Failed to retrieve account number for account name '${account_name}'." >&2
  exit 1
fi

echo "Account name is: ${account_name}, and account number is: ${account_number}"
echo "Environment: ${env}"

# Construct App Deployer role ARN
app_deployer_role_arn="arn:aws:iam::${account_number}:role/COMMSAppDeployer"

# Attempt to assume role
if ! session_tokens=($(aws sts assume-role \
  --role-arn "${app_deployer_role_arn}" \
  --role-session-name "comms-pipeline" \
  --query Credentials \
  --output text 2>/dev/null)); then
  echo "Error: STS Assume Role request failed for role '${app_deployer_role_arn}'." >&2
  exit 1
fi

# Export session tokens
export AWS_ACCESS_KEY_ID="${session_tokens[0]}"
export AWS_SECRET_ACCESS_KEY="${session_tokens[2]}"
export AWS_SESSION_TOKEN="${session_tokens[3]}"
export AWS_SESSION_EXPIRY="${session_tokens[1]}"
export AWS_ACCOUNT_ID="${account_number}"
export ACCOUNT_NAME="${account_name}"

# Validate AWS session tokens
if [[ -n "${AWS_ACCESS_KEY_ID}" && -n "${AWS_SECRET_ACCESS_KEY}" && -n "${AWS_SESSION_TOKEN}" ]]; then
  echo -e "Successfully assumed the role '${app_deployer_role_arn}'.\n"
else
  echo "Error: Failed to assume the role '${app_deployer_role_arn}'." >&2
  exit 1
fi
