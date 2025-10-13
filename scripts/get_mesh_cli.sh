#!/bin/bash
# Usage: ./import_package.sh <repo_url> <package_dir_in_repo> <target_dir_in_current_repo> [branch]

REPO_URL="https://github.com/NHSDigital/comms-mgr.git"
PACKAGE_DIR="packages/libs/mesh-cli"
TARGET_DIR="/helpers/mesh-cli"
BRANCH="${4:-main}"  # default branch

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR" || exit 1

# Initialize empty git repo quietly
git init -q

# Add remote quietly
git remote add origin "$REPO_URL"

# Enable sparse checkout quietly
git sparse-checkout init --cone
git sparse-checkout set "$PACKAGE_DIR" >/dev/null 2>&1

# Pull only the branch quietly
git pull --quiet origin "$BRANCH"

# Copy package into existing repo
mkdir -p "$OLDPWD/$TARGET_DIR"
cp -r "$PACKAGE_DIR/." "$OLDPWD/$TARGET_DIR/"

# Cleanup
cd "$OLDPWD"
rm -rf "$TEMP_DIR"

echo "$MESH_CLIENT_CONFIG" > helpers/mesh-cli/client_config.json

pip install -e .
