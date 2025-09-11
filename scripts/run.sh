#!/usr/bin/env bash

set -uo pipefail

if [ -z "$API_ENVIRONMENT" ]; then
  echo "Error: API_ENVIRONMENT is not set."
  exit 1
fi

source bash_assume_role.sh ${API_ENVIRONMENT} ./scripts

python -m venv .venv

source .venv/bin/activate
poetry install

poetry run pytest
