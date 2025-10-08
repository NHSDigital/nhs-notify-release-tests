#!/bin/bash

# File to store state (so it persists between runs in the same shell)
STATE_FILE="/tmp/aws_env_state"

toggle_aws_env() {
    if [[ -n "$AWS_ACCESS_KEY_ID" && -z "$AWS_ENV_BACKUP" ]]; then
        # Backup current values
        export AWS_ACCESS_KEY_ID_BACKUP="$AWS_ACCESS_KEY_ID"
        export AWS_SECRET_ACCESS_KEY_BACKUP="$AWS_SECRET_ACCESS_KEY"
        export AWS_SESSION_TOKEN_BACKUP="$AWS_SESSION_TOKEN"
        export AWS_ENV_BACKUP=1

        # Unset them (defaults to mgmt account)
        unset AWS_ACCESS_KEY_ID
        unset AWS_SECRET_ACCESS_KEY
        unset AWS_SESSION_TOKEN
        echo "AWS environment variables unset (backed up)."

    elif [[ -n "$AWS_ENV_BACKUP" ]]; then
        # Restore from backup
        export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID_BACKUP"
        export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY_BACKUP"
        export AWS_SESSION_TOKEN="$AWS_SESSION_TOKEN_BACKUP"

        # Clean up backup markers
        unset AWS_ACCESS_KEY_ID_BACKUP
        unset AWS_SECRET_ACCESS_KEY_BACKUP
        unset AWS_SESSION_TOKEN_BACKUP
        unset AWS_ENV_BACKUP

        echo "AWS environment variables restored."
    else
        echo "No AWS environment variables found to unset."
    fi
}