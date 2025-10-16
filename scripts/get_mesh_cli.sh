#!/bin/bash
set -euo pipefail

REPO_URL="https://github.com/NHSDigital/comms-mgr.git"
PACKAGE_DIR="packages/libs/mesh-cli"
TARGET_DIR="helpers/mesh-cli"
BRANCH="${4:-main}"
VENV_PATH=".venv"

# --- Helper for logging ---
log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $*"
}

# --- If mesh-cli already exists, skip clone ---
if [ -d "$TARGET_DIR" ]; then
  log "Directory '$TARGET_DIR' already exists — skipping clone."
else
  log "Cloning mesh-cli from $REPO_URL (branch: $BRANCH)..."

  TEMP_DIR=$(mktemp -d)
  cd "$TEMP_DIR" || exit 1

  git init -q
  git remote add origin "$REPO_URL"
  git sparse-checkout init --cone
  git sparse-checkout set "$PACKAGE_DIR" >/dev/null 2>&1
  git pull origin "$BRANCH" --depth=1

  mkdir -p "$OLDPWD/$TARGET_DIR"
  cp -r "$PACKAGE_DIR/." "$OLDPWD/$TARGET_DIR/"

  cd "$OLDPWD"
  rm -rf "$TEMP_DIR"

  log "mesh-cli package copied to '$TARGET_DIR'."
fi

# --- Create MESH client config file ---
log "Writing MESH client config file..."
echo "$MESH_CLIENT_CONFIG" > "$TARGET_DIR/client_config.json"

# --- Build mesh-cli dependencies ---
cd "$TARGET_DIR"
if [ -f "Makefile" ]; then
  log "Running make install..."
  make install
fi
cd "$OLDPWD"

# --- Set up or reuse virtual environment ---
if [ ! -d "$VENV_PATH" ]; then
  log "Creating Python virtual environment at '$VENV_PATH'..."
  python3 -m venv "$VENV_PATH"
else
  log "Using existing virtual environment at '$VENV_PATH'."
fi

# --- Install mesh-cli into the virtual environment ---
log "Installing mesh-cli package into virtual environment..."
"$VENV_PATH/bin/pip" install -e "$TARGET_DIR"

log "mesh-cli installation complete."

log "Setup complete."
