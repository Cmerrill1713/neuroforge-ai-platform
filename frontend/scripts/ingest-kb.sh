#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
KB_DIR="$ROOT_DIR/knowledge_base"

if [[ ! -d "$KB_DIR" ]]; then
  echo "Knowledge base directory not found: $KB_DIR" >&2
  exit 1
fi

python "$ROOT_DIR/tools/manage_kb.py" rebuild
