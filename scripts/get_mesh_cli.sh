#!/bin/bash
#Check if directory exists already
if [ -d "helpers/mesh-cli" ]; then
  echo "Directory already exists"
else
    # Variables
    REPO_URL="https://github.com/NHSDigital/comms-mgr.git"
    PACKAGE_DIR="packages/libs/mesh-cli"
    TARGET_DIR="helpers/mesh-cli"
    BRANCH="${4:-main}"

    # Create a temporary directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR" || exit 1

    # Initialize empty git repo
    git init

    # Add remote
    git remote add origin "$REPO_URL"

    # Enable sparse checkout
    git sparse-checkout init --cone
    git sparse-checkout set "$PACKAGE_DIR" >/dev/null 2>&1

    git pull origin "$BRANCH"

    # Copy package into existing repo
    mkdir -p "$OLDPWD/$TARGET_DIR"
    cp -r "$PACKAGE_DIR/." "$OLDPWD/$TARGET_DIR/"

    # Cleanup
    cd "$OLDPWD"
    rm -rf "$TEMP_DIR"

    # Create a config file from environment variables
    echo "$MESH_CLIENT_CONFIG" > helpers/mesh-cli/client_config.json

    # Install the package
    pip install -e .
fi