#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.codex/skills/shipcheck"

if [[ -e "${TARGET_DIR}" ]]; then
  echo "Target already exists: ${TARGET_DIR}"
  echo "Move it aside before reinstalling."
  exit 1
fi

mkdir -p "$(dirname "${TARGET_DIR}")"
mkdir -p "${TARGET_DIR}"

if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude ".git" --exclude "__pycache__" --exclude ".DS_Store" "${ROOT_DIR}/" "${TARGET_DIR}/"
else
  cp -R "${ROOT_DIR}/." "${TARGET_DIR}/"
  rm -rf "${TARGET_DIR}/.git" "${TARGET_DIR}/__pycache__" "${TARGET_DIR}/.DS_Store"
fi

echo "Installed Shipcheck to ${TARGET_DIR}"
