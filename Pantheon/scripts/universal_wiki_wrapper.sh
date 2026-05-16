#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: universal_wiki_wrapper.sh <target_dir>"
  exit 1
fi

TARGET_DIR="$1"

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: target directory does not exist: $TARGET_DIR"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORG_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WIKI_DEST="$ORG_ROOT/wiki/codebase/$(basename "$TARGET_DIR")"

mkdir -p "$WIKI_DEST"

find "$TARGET_DIR" \
  -type f \
  -not -path "*/.git/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/target/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/.venv/*" \
  -not -path "*/__pycache__/*" \
  | while IFS= read -r FILE; do
    FILENAME="$(basename "$FILE")"
    REL_PATH="${FILE#$TARGET_DIR/}"
    EXT="${FILENAME##*.}"
    if [ "$EXT" = "$FILENAME" ]; then
      LANG_TAG=""
    else
      LANG_TAG="$EXT"
    fi
    SAFE_NAME="$(echo "$REL_PATH" | sed 's#[/ ]#_#g' | tr '.' '_')"
    WIKI_FILE="$WIKI_DEST/${SAFE_NAME}.md"
    {
      echo "# Artifact: $FILENAME"
      echo ""
      echo "**Source Path:** \`$FILE\`"
      echo ""
      echo "**Relative Path:** \`$REL_PATH\`"
      echo ""
      echo "\`\`\`$LANG_TAG"
      cat "$FILE"
      echo ""
      echo "\`\`\`"
    } > "$WIKI_FILE"
  done

echo "Execution Complete: All artifacts successfully wrapped in .md and archived to $WIKI_DEST"
