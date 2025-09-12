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

# Echo each required variable individually for debug
for VAR in "${REQUIRED_VARS[@]}"; do
  if [ "$VAR" != "PRIVATE_KEY_CONTENTS" ]; then
    echo "$VAR: ${!VAR}"
  fi
done

source ./scripts/bash_assume_role.sh ${account_id} ./scripts

# Echo first line of PRIVATE_KEY_CONTENTS
echo $PRIVATE_KEY_CONTENTS
echo $PRIVATE_KEY_CONTENTS > ./private.key
cat ./private.key

export PRIVATE_KEY=./private.key

python -m venv .venv

source .venv/bin/activate
poetry install

poetry run pytest
