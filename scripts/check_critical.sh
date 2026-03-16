#!/usr/bin/env bash
# Quick automated checks (no AI needed)
# Checks for common critical issues in diff files
#
# Usage: check_critical.sh <diff-file>
#
# Exit codes:
#   0 - All checks passed
#   1 - Critical issues found

set -e

DIFF_FILE="${1:?Usage: $0 <diff-file>}"

if [[ ! -f "$DIFF_FILE" ]]; then
  echo "Error: Diff file not found: $DIFF_FILE" >&2
  exit 1
fi

# Track if any issues found
ISSUES_FOUND=0

echo "🔍 Running automated checks on $DIFF_FILE..."
echo ""

# Check for secrets (basic patterns)
echo "Checking for secrets..."
if grep -qE '(api[_-]?key|password|secret|token).*[:=].*["\'][^"\']{8,}["\']' "$DIFF_FILE" 2>/dev/null; then
  echo "  ⚠️  Possible secret detected in changes"
  echo "     Pattern: api_key/password/secret/token with value"
  ISSUES_FOUND=1
fi

# Check for AWS keys
if grep -qE 'AKIA[0-9A-Z]{16}' "$DIFF_FILE" 2>/dev/null; then
  echo "  ⚠️  AWS access key detected"
  ISSUES_FOUND=1
fi

# Check for GitHub tokens
if grep -qE 'gh[ps]_[a-zA-Z0-9]{36}' "$DIFF_FILE" 2>/dev/null; then
  echo "  ⚠️  GitHub token detected"
  ISSUES_FOUND=1
fi

# Check for private keys
if grep -qE '-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----' "$DIFF_FILE" 2>/dev/null; then
  echo "  ⚠️  Private key detected"
  ISSUES_FOUND=1
fi

# Check for console.log in added lines
echo "Checking for console.log..."
if grep -qE '^\+.*console\.(log|debug|info)' "$DIFF_FILE" 2>/dev/null; then
  COUNT=$(grep -cE '^\+.*console\.(log|debug|info)' "$DIFF_FILE" 2>/dev/null || echo "0")
  echo "  ⚠️  Found $COUNT console.log statement(s) in changes"
  ISSUES_FOUND=1
fi

# Check for debugger statements
echo "Checking for debugger statements..."
if grep -qE '^\+.*\bdebugger\b' "$DIFF_FILE" 2>/dev/null; then
  echo "  ⚠️  debugger statement found"
  ISSUES_FOUND=1
fi

# Check for TODO/FIXME (warning only, don't block)
echo "Checking for TODO/FIXME..."
if grep -qE '^\+.*(TODO|FIXME|XXX):' "$DIFF_FILE" 2>/dev/null; then
  COUNT=$(grep -cE '^\+.*(TODO|FIXME|XXX):' "$DIFF_FILE" 2>/dev/null || echo "0")
  echo "  ℹ️  Found $COUNT TODO/FIXME comment(s) (warning only)"
fi

# Check for merge conflict markers
echo "Checking for merge conflicts..."
if grep -qE '^(\+.*)?(<<<<<<<|=======|>>>>>>>)' "$DIFF_FILE" 2>/dev/null; then
  echo "  ⚠️  Merge conflict markers found"
  ISSUES_FOUND=1
fi

# Check for trailing whitespace in added lines
echo "Checking for trailing whitespace..."
if grep -qE '^\+.*[[:space:]]$' "$DIFF_FILE" 2>/dev/null; then
  COUNT=$(grep -cE '^\+.*[[:space:]]$' "$DIFF_FILE" 2>/dev/null || echo "0")
  echo "  ℹ️  Found $COUNT line(s) with trailing whitespace (warning only)"
fi

echo ""

# Summary
if [[ $ISSUES_FOUND -eq 0 ]]; then
  echo "✅ All automated checks passed"
  exit 0
else
  echo "❌ Critical issues found!"
  echo ""
  echo "Recommendations:"
  echo "  - Remove secrets (use environment variables)"
  echo "  - Remove console.log and debugger statements"
  echo "  - Resolve merge conflicts"
  echo ""
  echo "To run full AI review:"
  echo "  Ask your AI agent: 'Review .review/diff.txt'"
  echo ""
  echo "To bypass (not recommended):"
  echo "  git commit --no-verify"
  exit 1
fi
