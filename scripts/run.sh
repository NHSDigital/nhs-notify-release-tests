#!/usr/bin/env bash

set -uo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <account_id> <environment>" >&2
  exit 1
fi
ACCOUNT_ID="$1"
ENVIRONMENT="$2"
export ENVIRONMENT
export ACCOUNT_ID

source ./scripts/bash_assume_role.sh ${ACCOUNT_ID} ./scripts

echo $PRIVATE_KEY_CONTENTS > ./private.key
export PRIVATE_KEY=./private.key

API_ENVIRONMENT=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/api-environment" --with-decryption --query "Parameter.Value" --output text) && export API_ENVIRONMENT
API_KEY=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/api-key" --with-decryption --query "Parameter.Value" --output text) && export API_KEY
BASE_URL=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/base-url" --with-decryption --query "Parameter.Value" --output text) && export BASE_URL
GUKN_API_KEY=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/gukn-api-key" --with-decryption --query "Parameter.Value" --output text) && export GUKN_API_KEY
NHS_APP_OTP=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/nhs-app-otp" --with-decryption --query "Parameter.Value" --output text) && export NHS_APP_OTP
NHS_APP_PASSWORD=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/nhs-app-password" --with-decryption --query "Parameter.Value" --output text) && export NHS_APP_PASSWORD
NHS_APP_USERNAME=$(aws ssm get-parameter --name "/comms/${ENVIRONMENT}/release-tests/nhs-app-username" --with-decryption --query "Parameter.Value" --output text) && export NHS_APP_USERNAME

python -m venv .venv

source .venv/bin/activate
poetry install

poetry run pytest

unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

S3_BUCKET="$OUTPUT_BUCKET"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
S3_PREFIX="release-tests/${ENVIRONMENT}/${TIMESTAMP}/"

if [ -d "tests/evidence" ]; then
  echo "Uploading evidence to s3://${S3_BUCKET}/${S3_PREFIX}"
  aws s3 cp tests/evidence/ "s3://${S3_BUCKET}/${S3_PREFIX}" --recursive
else
  echo "No evidence directory found to upload."
fi