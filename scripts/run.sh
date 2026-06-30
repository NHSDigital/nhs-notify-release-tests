#!/usr/bin/env bash

set -uo pipefail

get_ssm_parameter_value() {
  local parameter_name="$1"

  aws ssm get-parameter \
    --name "$parameter_name" \
    --with-decryption \
    --query "Parameter.Value" \
    --output text 2>/dev/null
}

get_release_test_secret() {
  local secret_name="$1"
  local primary_parameter="/comms/${ENVIRONMENT}/release-tests/${secret_name}"
  local fallback_environment="${RELEASE_TESTS_CONFIG_FALLBACK_ENVIRONMENT:-}"
  local fallback_parameter=""
  local value

  if [ -z "$fallback_environment" ] && [ "$ENVIRONMENT" = "ref" ]; then
    fallback_environment="uat"
  fi

  if [ -n "$fallback_environment" ]; then
    fallback_parameter="/comms/${fallback_environment}/release-tests/${secret_name}"
  fi

  value=$(get_ssm_parameter_value "$primary_parameter")
  if [ -n "$value" ] && [ "$value" != "None" ]; then
    printf '%s' "$value"
    return 0
  fi

  if [ -n "$fallback_environment" ] && [ "$ENVIRONMENT" != "$fallback_environment" ]; then
    value=$(get_ssm_parameter_value "$fallback_parameter")
    if [ -n "$value" ] && [ "$value" != "None" ]; then
      echo "Using fallback release test config from ${fallback_parameter}" >&2
      printf '%s' "$value"
      return 0
    fi
  fi

  return 1
}

default_base_url() {
  case "$ENVIRONMENT" in
    int|ref|uat)
      printf 'https://%s.api.service.nhs.uk/comms' "$ENVIRONMENT"
      ;;
    internal-qa)
      printf 'https://internal-qa.api.service.nhs.uk/comms'
      ;;
    *)
      return 1
      ;;
  esac
}

# Get Github PAT
GH_TOKEN=$(aws ssm get-parameter --name "/comms-pl/github/pl-mgmt/personal-access-token" --with-decryption --query "Parameter.Value" --output text) && export GH_TOKEN

# Assume AWS role for the given account
source ./scripts/bash_assume_role.sh ${ACCOUNT_ID} ./scripts

# Fetch secrets and configuration from AWS SSM Parameter Store in the target account.
# Ref can reuse the shared release test secrets from uat, but it must still target ref APIs/resources.
API_ENVIRONMENT=$(get_ssm_parameter_value "/comms/${ENVIRONMENT}/release-tests/api-environment")
if [ -z "${API_ENVIRONMENT:-}" ] || [ "$API_ENVIRONMENT" = "None" ]; then
  API_ENVIRONMENT="$ENVIRONMENT"
fi
export API_ENVIRONMENT

BASE_URL=$(get_ssm_parameter_value "/comms/${ENVIRONMENT}/release-tests/base-url")
if [ -z "${BASE_URL:-}" ] || [ "$BASE_URL" = "None" ]; then
  BASE_URL=$(default_base_url)
fi
export BASE_URL

API_KEY=$(get_release_test_secret "api-key") && export API_KEY
GUKN_API_KEY=$(get_release_test_secret "gukn-api-key") && export GUKN_API_KEY
NHS_APP_OTP=$(get_release_test_secret "nhs-app-otp") && export NHS_APP_OTP
NHS_APP_PASSWORD=$(get_release_test_secret "nhs-app-password") && export NHS_APP_PASSWORD
NHS_APP_USERNAME=$(get_release_test_secret "nhs-app-username") && export NHS_APP_USERNAME
PRIVATE_KEY_CONTENTS=$(get_release_test_secret "private-key") && export PRIVATE_KEY_CONTENTS
printf '%s' "$PRIVATE_KEY_CONTENTS" > ./private.key
export PRIVATE_KEY=./private.key
MESH_CLIENT_CONFIG_CONTENTS=$(get_release_test_secret "mesh-client-config") && export MESH_CLIENT_CONFIG_CONTENTS
printf '%s' "$MESH_CLIENT_CONFIG_CONTENTS" > ./client_config.json
export MESH_CLIENT_CONFIG=./client_config.json

if [ -z "${CLIENT:-}" ]; then
  if [ "$API_ENVIRONMENT" = "int" ]; then
    export CLIENT="apim_integration_test"
  else
    export CLIENT="apim_integration_test_client_id"
  fi
fi

# Check for presence of all required exported variables
REQUIRED_VARS=(ACCOUNT_ID ENVIRONMENT API_ENVIRONMENT API_KEY BASE_URL GUKN_API_KEY NHS_APP_OTP NHS_APP_PASSWORD NHS_APP_USERNAME MESH_CLIENT_CONFIG OUTPUT_BUCKET PRIVATE_KEY PRIVATE_KEY_CONTENTS)
missing_vars=()
for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR:-}" ]; then
    missing_vars+=("$VAR")
  fi
done
if [ ${#missing_vars[@]} -ne 0 ]; then
  echo "Error: The following required variables are not set: ${missing_vars[*]}" >&2
  exit 1
else
  echo "All required environment variables are set."
fi

# Set up Python virtual environment and install dependencies
python -m venv .venv \
  && source .venv/bin/activate \
  && poetry install

# Run pytest, capturing the exit code so it can be preserved after the S3 upload
set +e
poetry run pytest --html=tests/evidence/report.html --self-contained-html --capture=tee-sys
PYTEST_EXIT_CODE=$?
set -e

# Unset AWS credentials to drop back to default profile
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN

# Upload test evidence to S3 with environment/timestamp prefix
# This always runs regardless of test outcome so the report is always available
TIMESTAMP=$(date +%Y%m%d%H%M%S)
S3_PREFIX="release-tests/${ENVIRONMENT}/${TIMESTAMP}/"

if [ -d "tests/evidence" ]; then
  echo "Uploading evidence to s3://${OUTPUT_BUCKET}/${S3_PREFIX}"
  aws s3 cp tests/evidence/ "s3://${OUTPUT_BUCKET}/${S3_PREFIX}" --recursive
else
  echo "No evidence directory found to upload."
fi

# Exit with pytest's code so the container exit code reflects the test result
exit $PYTEST_EXIT_CODE
