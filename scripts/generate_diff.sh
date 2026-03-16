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
# Options:
#   --allow-secrets    Disable secret detection (use with caution)
#   --no-filter        Disable noise filtering (include all files)
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

# Default exclusion patterns (industry standard - filters noise from diffs)
EXCLUDES=(
  # Lock files
  ':!**/*lock.json' ':!**/*lock.yaml' ':!**/*.lock'
  ':!**/package-lock.json' ':!**/yarn.lock' ':!**/pnpm-lock.yaml'
  ':!**/Gemfile.lock' ':!**/poetry.lock' ':!**/Cargo.lock'
  ':!**/composer.lock' ':!**/Pipfile.lock' ':!**/go.sum'
  
  # Binary & media files
  ':!**/*.svg' ':!**/*.png' ':!**/*.jpg' ':!**/*.jpeg' 
  ':!**/*.gif' ':!**/*.ico' ':!**/*.webp' ':!**/*.pdf'
  ':!**/*.woff' ':!**/*.woff2' ':!**/*.ttf' ':!**/*.eot'
  
  # Minified/compiled files
  ':!**/*.min.js' ':!**/*.min.css' ':!**/*.bundle.js'
  ':!**/*.chunk.js' ':!**/*.chunk.css'
  
  # Build outputs & dependencies
  ':!dist/**' ':!build/**' ':!out/**' ':!.next/**'
  ':!node_modules/**' ':!vendor/**' ':!target/**'
  ':!__pycache__/**' ':!*.pyc' ':!.venv/**'
  
  # Logs & temp files
  ':!*.log' ':!*.tmp' ':!*.cache' ':!.DS_Store'
)

# Load custom configuration if exists
CONFIG_FILE="$REPO_ROOT/.reviewrc"
ALLOW_SECRETS=false
NO_FILTER=false

if [[ -f "$CONFIG_FILE" ]]; then
  echo "Loading configuration from .reviewrc" >&2
  # Parse JSON config for additional excludes (simple grep-based parsing)
  # Note: For complex JSON parsing, use jq if available
  if command -v jq &> /dev/null; then
    # Use :(exclude) to avoid pathspec magic issues (e.g. :! with __pycache__ can break exclusions)
    ADDITIONAL_PATTERNS=$(jq -r '.ignorePatterns[]? // empty' "$CONFIG_FILE" 2>/dev/null | sed 's/^/:(exclude)**\//')
    if [[ -n "$ADDITIONAL_PATTERNS" ]]; then
      while IFS= read -r pattern; do
        EXCLUDES+=("$pattern")
      done <<< "$ADDITIONAL_PATTERNS"
      echo "Loaded $(echo "$ADDITIONAL_PATTERNS" | wc -l | tr -d ' ') custom ignore patterns" >&2
    fi
  fi
fi

# Parse flags
while [[ $# -gt 0 ]]; do
  case $1 in
    --allow-secrets)
      ALLOW_SECRETS=true
      shift
      ;;
    --no-filter)
      NO_FILTER=true
      EXCLUDES=()
      shift
      ;;
    *)
      break
      ;;
  esac
done

# --staged: only staged changes
if [[ "$1" == "--staged" ]]; then
  OUT="${2:-$DEFAULT_OUT}"
  echo "Writing staged diff to $OUT" >&2
  if [[ "$NO_FILTER" == true ]]; then
    git --no-pager diff --cached > "$OUT"
  else
    git --no-pager diff --cached "${EXCLUDES[@]}" > "$OUT"
  fi
  if [[ ! -s "$OUT" ]]; then
    echo "No staged changes." >&2
    exit 0
  fi
  
  # Secret detection
  if [[ "$ALLOW_SECRETS" == false ]]; then
    if command -v python3 &> /dev/null && [[ -f "$REPO_ROOT/scripts/filters/secret_detector.py" ]]; then
      python3 "$REPO_ROOT/scripts/filters/secret_detector.py" "$OUT"
      if [[ $? -ne 0 ]]; then
        echo "⚠️  Secrets detected! Review blocked. Use --allow-secrets to override (not recommended)." >&2
        exit 1
      fi
    fi
  fi
  
  echo "Done. $(wc -l < "$OUT") lines in $OUT" >&2
  exit 0
fi

# --local: all local changes vs HEAD
if [[ "$1" == "--local" ]]; then
  OUT="${2:-$DEFAULT_OUT}"
  echo "Writing all local changes (vs HEAD) to $OUT" >&2
  if [[ "$NO_FILTER" == true ]]; then
    git --no-pager diff HEAD > "$OUT"
  else
    git --no-pager diff HEAD "${EXCLUDES[@]}" > "$OUT"
  fi
  if [[ ! -s "$OUT" ]]; then
    echo "No local changes (working tree clean)." >&2
    exit 0
  fi
  
  # Secret detection
  if [[ "$ALLOW_SECRETS" == false ]]; then
    if command -v python3 &> /dev/null && [[ -f "$REPO_ROOT/scripts/filters/secret_detector.py" ]]; then
      python3 "$REPO_ROOT/scripts/filters/secret_detector.py" "$OUT"
      if [[ $? -ne 0 ]]; then
        echo "⚠️  Secrets detected! Review blocked. Use --allow-secrets to override (not recommended)." >&2
        exit 1
      fi
    fi
  fi
  
  echo "Done. $(wc -l < "$OUT") lines in $OUT" >&2
  exit 0
fi

# Branch vs branch (committed only)
BASE="${1:?Usage: $0 <base-branch> <feature-branch> [output-file]
      Or: $0 --staged [output-file]
      Or: $0 --local [output-file]
      Options: --allow-secrets --no-filter}"
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
if [[ "$NO_FILTER" == true ]]; then
  git --no-pager diff "$BASE..$FEATURE" > "$OUT"
else
  git --no-pager diff "$BASE..$FEATURE" "${EXCLUDES[@]}" > "$OUT"
fi

if [[ ! -s "$OUT" ]]; then
  echo "No changes between $BASE and $FEATURE." >&2
  exit 0
fi

# Secret detection
if [[ "$ALLOW_SECRETS" == false ]]; then
  if command -v python3 &> /dev/null && [[ -f "$REPO_ROOT/scripts/filters/secret_detector.py" ]]; then
    python3 "$REPO_ROOT/scripts/filters/secret_detector.py" "$OUT"
    if [[ $? -ne 0 ]]; then
      echo "⚠️  Secrets detected! Review blocked. Use --allow-secrets to override (not recommended)." >&2
      exit 1
    fi
  fi
fi

echo "Done. $(wc -l < "$OUT") lines in $OUT" >&2
