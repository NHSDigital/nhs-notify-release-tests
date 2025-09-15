#!/usr/bin/env bash

set -uo pipefail

# Check for required arguments
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <account_id> <environment>" >&2
  exit 1
fi
ACCOUNT_ID="$1"
ENVIRONMENT="$2"
export ENVIRONMENT
export ACCOUNT_ID

# Assume AWS role for the given account
source ./scripts/bash_assume_role.sh ${ACCOUNT_ID} ./scripts

# Write private key contents to file and export its path
# PRIVATE_KEY_CONTENTS should be set in the environment
echo $PRIVATE_KEY_CONTENTS > ./private.key
export PRIVATE_KEY=./private.key

# Fetch secrets and configuration from AWS SSM Parameter Store
API_ENVIRONMENT=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/api-environment" --with-decryption --query "Parameter.Value" --output text) && export API_ENVIRONMENT
API_KEY=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/api-key" --with-decryption --query "Parameter.Value" --output text) && export API_KEY
BASE_URL=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/base-url" --with-decryption --query "Parameter.Value" --output text) && export BASE_URL
GUKN_API_KEY=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/gukn-api-key" --with-decryption --query "Parameter.Value" --output text) && export GUKN_API_KEY
NHS_APP_OTP=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/nhs-app-otp" --with-decryption --query "Parameter.Value" --output text) && export NHS_APP_OTP
NHS_APP_PASSWORD=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/nhs-app-password" --with-decryption --query "Parameter.Value" --output text) && export NHS_APP_PASSWORD
NHS_APP_USERNAME=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/nhs-app-username" --with-decryption --query "Parameter.Value" --output text) && export NHS_APP_USERNAME

# Set up Python virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
poetry install

# Run tests
poetry run pytest

# Unset AWS credentials to drop back to default profile
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

# Upload test evidence to S3 with environment/timestamp prefix
S3_BUCKET="$OUTPUT_BUCKET"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
S3_PREFIX="release-tests/${ENVIRONMENT}/${TIMESTAMP}/"

if [ -d "tests/evidence" ]; then
  echo "Uploading evidence to s3://${S3_BUCKET}/${S3_PREFIX}"
  aws s3 cp tests/evidence/ "s3://${S3_BUCKET}/${S3_PREFIX}" --recursive
else
  echo "No evidence directory found to upload."
fi