#!/usr/bin/env bash
# Generate full diff (no pager) and write to a file. Output is under .review/ so git ignores it.
#
# Committed changes (default):
#   generate_diff.sh <base-branch> <feature-branch> [output-file]
#   e.g. generate_diff.sh develop my-branch
#
# Staged changes only (vs HEAD):
#   generate_diff.sh --staged [output-file]
#
# All local changes (staged + unstaged vs HEAD):
#   generate_diff.sh --local [output-file]
#
# Default output: .review/diff.txt (directory .review/ is in .gitignore)
#
set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: not inside a git repository." >&2
  exit 1
}
cd "$REPO_ROOT"

REVIEW_DIR="$REPO_ROOT/.review"
DEFAULT_OUT="$REVIEW_DIR/diff.txt"
mkdir -p "$REVIEW_DIR"

if ! grep -qxF '.review/' "$REPO_ROOT/.gitignore" 2>/dev/null; then
  echo '.review/' >> "$REPO_ROOT/.gitignore"
  echo "Added .review/ to .gitignore" >&2
fi

# --staged: only staged changes
if [[ "$1" == "--staged" ]]; then
  OUT="${2:-$DEFAULT_OUT}"
  echo "Writing staged diff to $OUT" >&2
  git --no-pager diff --cached > "$OUT"
  if [[ ! -s "$OUT" ]]; then
    echo "No staged changes." >&2
    exit 0
  fi
  echo "Done. $(wc -l < "$OUT") lines in $OUT" >&2
  exit 0
fi

# --local: all local changes vs HEAD
if [[ "$1" == "--local" ]]; then
  OUT="${2:-$DEFAULT_OUT}"
  echo "Writing all local changes (vs HEAD) to $OUT" >&2
  git --no-pager diff HEAD > "$OUT"
  if [[ ! -s "$OUT" ]]; then
    echo "No local changes (working tree clean)." >&2
    exit 0
  fi
  echo "Done. $(wc -l < "$OUT") lines in $OUT" >&2
  exit 0
fi

# Branch vs branch (committed only)
BASE="${1:?Usage: $0 <base-branch> <feature-branch> [output-file]
      Or: $0 --staged [output-file]
      Or: $0 --local [output-file]}"
FEATURE="${2:?Usage: $0 <base-branch> <feature-branch> [output-file]}"
OUT="${3:-$DEFAULT_OUT}"

if ! git rev-parse --verify "$BASE" &>/dev/null; then
  echo "Error: base branch '$BASE' not found." >&2
  exit 1
fi
if ! git rev-parse --verify "$FEATURE" &>/dev/null; then
  echo "Error: feature branch '$FEATURE' not found." >&2
  exit 1
fi

echo "Writing diff $BASE..$FEATURE to $OUT" >&2
git --no-pager diff "$BASE..$FEATURE" > "$OUT"

if [[ ! -s "$OUT" ]]; then
  echo "No changes between $BASE and $FEATURE." >&2
  exit 0
fi

echo "Done. $(wc -l < "$OUT") lines in $OUT" >&2
