#!/usr/bin/env bash

set -uo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <account_id>" >&2
  exit 1
fi
account_id="$1"

REQUIRED_VARS=(API_ENVIRONMENT BASE_URL API_KEY PRIVATE_KEY_CONTENTS GUKN_API_KEY NHS_APP_USERNAME NHS_APP_PASSWORD NHS_APP_OTP ENVIRONMENT)
for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR:-}" ]; then
    echo "Error: $VAR is not set."
    exit 1
  fi
done

source ./scripts/bash_assume_role.sh ${account_id} ./scripts

echo $PRIVATE_KEY_CONTENTS > ./private.key
export PRIVATE_KEY=./private.key

python -m venv .venv

source .venv/bin/activate
poetry install

poetry run pytest
