#!/usr/bin/env bash

set -euo pipefail

# Validate input arguments
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <account_name>" >&2
    exit 1
fi

ACCOUNT_NAME="$1"

# Function to check parameter validity
function check_parameter {
    if [[ -z "$2" ]]; then
        echo "Error: Missing input for '$1'" >&2
        exit 1
    fi
}

# Define account list
declare -A accountList
accountList[identities]="347250048819"
accountList[comms-pl-mdev]="422073736876"
accountList[comms-pl-mgmt]="886194799418"
accountList[comms-mgr-dev]="257995483745"
accountList[comms-mgr-dev2]="637423498933"
accountList[comms-mgr-test]="736102632839"
accountList[comms-mgr-perf-mock]="228720325595"
accountList[comms-mgr-perftest]="815490582396"
accountList[comms-mgr-perf-mck2]="021891570951"
accountList[comms-mgr-perftest2]="021891570814"
accountList[comms-mgr-prod]="746418818434"
accountList[comms-mgr-preprod]="975049913032"

# Ensure account name is not empty
check_parameter "Account Name" "$ACCOUNT_NAME"

# Check if account name exists in the account list
if [[ ! -v accountList["$ACCOUNT_NAME"] ]]; then
    echo "Error: Account name '$ACCOUNT_NAME' not found in account list." >&2
    exit 1
fi

# Retrieve and print the account number
account_number="${accountList[$ACCOUNT_NAME]}"
echo "$account_number"
