#!/usr/bin/env bash

set -uo pipefail

REQUIRED_VARS=(API_ENVIRONMENT BASE_URL API_KEY PRIVATE_KEY GUKN_API_KEY NHS_APP_USERNAME NHS_APP_PASSWORD NHS_APP_OTP ENVIRONMENT)
for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR:-}" ]; then
    echo "Error: $VAR is not set."
    exit 1
  fi
done

lower_env="$(echo "$ENVIRONMENT" | tr '[:upper:]' '[:lower:]')"
source bash_assume_role.sh ${lower_env} ./scripts

python -m venv .venv

source .venv/bin/activate
poetry install

poetry run pytest
