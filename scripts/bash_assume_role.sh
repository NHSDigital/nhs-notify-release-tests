#!/usr/bin/env bash

###
# NOTE: _SOURCE_ this file in order to switch to the COMMSAppDeployer role in the correct account
###

set -uo pipefail

# Validate input arguments
account_id="${1:-}"
localdir="${2:-}"

if [[ -z "${account_id}" ]]; then
  echo "Error: Account ID is not provided." >&2
  exit 1
fi

if [[ -z "${localdir}" || ! -d "${localdir}" ]]; then
  echo "Error: Local directory (localdir) is not provided or is invalid." >&2
  exit 1
fi

echo "Account ID is: ${account_id}"

# Construct App Deployer role ARN
app_deployer_role_arn="arn:aws:iam::${account_id}:role/COMMSAppDeployer"

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
export AWS_ACCOUNT_ID="${account_id}"

# Validate AWS session tokens
if [[ -n "${AWS_ACCESS_KEY_ID}" && -n "${AWS_SECRET_ACCESS_KEY}" && -n "${AWS_SESSION_TOKEN}" ]]; then
  echo -e "Successfully assumed the role '${app_deployer_role_arn}'.\n"
else
  echo "Error: Failed to assume the role '${app_deployer_role_arn}'." >&2
  exit 1
fi
