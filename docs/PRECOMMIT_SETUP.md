# Pre-commit Hook Setup

Automatically run review-before-pr on staged changes before committing.

---

## Why Use Pre-commit Hooks?

Pre-commit hooks catch issues **before** they enter your commit history:

- ✅ Catch secrets before they're committed
- ✅ Block commits with critical issues
- ✅ Maintain code quality consistently
- ✅ Faster feedback loop (no waiting for CI)

---

## Quick Start

### Option 1: Using Husky (Node.js projects)

**1. Install Husky:**

```bash
npm install --save-dev husky
npx husky init
```

**2. Create pre-commit hook:**

```bash
cat > .husky/pre-commit << 'EOF'
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Run review on staged changes
SKILL_DIR=".cursor/skills/review-before-pr"

# Generate diff of staged changes
$SKILL_DIR/scripts/generate_diff.sh --staged

# Run automated checks (no AI needed)
$SKILL_DIR/scripts/check_critical.sh .review/diff.txt

if [ $? -ne 0 ]; then
  echo "❌ Critical issues found. Run full review or fix issues before committing."
  echo "   To review: Ask your AI agent to review .review/diff.txt"
  exit 1
fi

echo "✅ Pre-commit checks passed"
EOF

chmod +x .husky/pre-commit
```

**3. Test it:**

```bash
git add .
git commit -m "test"
# Hook will run automatically
```

---

### Option 2: Using pre-commit framework (Python projects)

**1. Install pre-commit:**

```bash
pip install pre-commit
# or
brew install pre-commit
```

**2. Create `.pre-commit-config.yaml`:**

```yaml
repos:
  - repo: local
    hooks:
      - id: review-before-pr
        name: Review staged changes
        entry: .cursor/skills/review-before-pr/scripts/precommit_hook.sh
        language: script
        pass_filenames: false
        stages: [commit]
```

**3. Create the hook script:**

```bash
cat > .cursor/skills/review-before-pr/scripts/precommit_hook.sh << 'EOF'
#!/bin/bash
set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Generate diff
$SKILL_DIR/scripts/generate_diff.sh --staged

# Run automated checks
$SKILL_DIR/scripts/check_critical.sh .review/diff.txt

exit $?
EOF

chmod +x .cursor/skills/review-before-pr/scripts/precommit_hook.sh
```

**4. Install the hook:**

```bash
pre-commit install
```

**5. Test it:**

```bash
git add .
git commit -m "test"
```

---

### Option 3: Manual Git Hook (Any project)

**1. Create hook file:**

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
set -e

SKILL_DIR=".cursor/skills/review-before-pr"

echo "🔍 Running pre-commit review..."

# Generate diff of staged changes
$SKILL_DIR/scripts/generate_diff.sh --staged

# Run automated checks
$SKILL_DIR/scripts/check_critical.sh .review/diff.txt

if [ $? -ne 0 ]; then
  echo ""
  echo "❌ Pre-commit checks failed!"
  echo "   Fix the issues above or run full AI review:"
  echo "   Ask your AI: 'Review .review/diff.txt'"
  echo ""
  echo "   To bypass (not recommended): git commit --no-verify"
  exit 1
fi

echo "✅ Pre-commit checks passed"
exit 0
EOF

chmod +x .git/hooks/pre-commit
```

**2. Test it:**

```bash
git add .
git commit -m "test"
```

---

## The Automated Check Script

The `check_critical.sh` script performs fast, automated checks without AI:

```bash
#!/usr/bin/env bash
# Quick automated checks (no AI needed)

DIFF_FILE="$1"

# Check for secrets
if grep -qE '(api[_-]?key|password|secret|token).*=.*["\'][^"\']+["\']' "$DIFF_FILE"; then
  echo "⚠️  Possible secret detected in staged changes"
  exit 1
fi

# Check for console.log (if configured)
if grep -qE '^\+.*console\.(log|debug)' "$DIFF_FILE"; then
  echo "⚠️  console.log found in staged changes"
  exit 1
fi

# Check for debugger statements
if grep -qE '^\+.*debugger' "$DIFF_FILE"; then
  echo "⚠️  debugger statement found"
  exit 1
fi

# Check for TODO/FIXME in new code
if grep -qE '^\+.*(TODO|FIXME|XXX):' "$DIFF_FILE"; then
  echo "⚠️  TODO/FIXME found in staged changes"
  # Warning only, don't block
fi

echo "✅ Basic checks passed"
exit 0
```

---

## Customization

### Skip Specific Checks

Edit `check_critical.sh` to disable checks you don't want:

```bash
# Comment out to disable
# if grep -qE '^\+.*console\.(log|debug)' "$DIFF_FILE"; then
#   echo "⚠️  console.log found"
#   exit 1
# fi
```

### Add Custom Checks

Add your own patterns:

```bash
# Check for hardcoded URLs
if grep -qE '^\+.*https?://localhost' "$DIFF_FILE"; then
  echo "⚠️  Hardcoded localhost URL found"
  exit 1
fi

# Check for missing tests
if git diff --cached --name-only | grep -qE '\.(ts|js)$'; then
  if ! git diff --cached --name-only | grep -qE '\.test\.(ts|js)$'; then
    echo "⚠️  Code changes without test changes"
    # Warning only
  fi
fi
```

### Full AI Review in Hook

For thorough pre-commit reviews (slower but comprehensive):

```bash
#!/bin/bash
set -e

SKILL_DIR=".cursor/skills/review-before-pr"

# Generate diff
$SKILL_DIR/scripts/generate_diff.sh --staged

# Ask AI to review (requires AI agent running)
echo "🤖 Running AI review..."

# This requires your AI agent to be running and accessible
# Implementation depends on your agent's CLI capabilities

# For now, just run automated checks
$SKILL_DIR/scripts/check_critical.sh .review/diff.txt

exit $?
```

---

## Configuration

### Skip Hook for Specific Commits

```bash
# Bypass hook for this commit only
git commit --no-verify -m "WIP: work in progress"
```

### Disable Hook Temporarily

```bash
# Rename to disable
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled

# Re-enable
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

### Configure in .reviewrc

```json
{
  "precommit": {
    "enabled": true,
    "blockOnSecrets": true,
    "blockOnConsoleLog": false,
    "blockOnDebugger": true,
    "warnOnTodo": true
  }
}
```

---

## Troubleshooting

### Hook not running

**1. Check if hook is executable:**
```bash
ls -la .git/hooks/pre-commit
# Should show -rwxr-xr-x (executable)

# If not:
chmod +x .git/hooks/pre-commit
```

**2. Verify hook location:**
```bash
# For Husky
ls -la .husky/pre-commit

# For git hooks
ls -la .git/hooks/pre-commit
```

**3. Test hook manually:**
```bash
.git/hooks/pre-commit
# or
.husky/pre-commit
```

---

### Hook fails with "command not found"

**Cause:** Script path is wrong

**Fix:**
```bash
# Update SKILL_DIR in hook to correct path
# For Cursor:
SKILL_DIR=".cursor/skills/review-before-pr"

# For Claude Code:
SKILL_DIR=".claude/skills/review-before-pr"
```

---

### Hook is too slow

**Cause:** Large diffs or complex checks

**Solutions:**

1. **Use only automated checks (no AI):**
   ```bash
   # Just run check_critical.sh
   $SKILL_DIR/scripts/check_critical.sh .review/diff.txt
   ```

2. **Skip for WIP commits:**
   ```bash
   git commit --no-verify -m "WIP"
   ```

3. **Run full review in CI instead:**
   - Keep pre-commit hooks fast (automated checks only)
   - Run full AI review in GitHub Actions/GitLab CI

---

### False positives

**Cause:** Check patterns too strict

**Fix:** Customize `check_critical.sh` patterns:

```bash
# More lenient secret detection
if grep -qE 'api_key\s*=\s*["\'][A-Za-z0-9]{32,}["\']' "$DIFF_FILE"; then
  # Only flag long alphanumeric strings
fi
```

---

## Best Practices

### 1. Start with Automated Checks Only

Don't run full AI review in pre-commit hooks initially:
- Automated checks are fast (< 1 second)
- Full AI review can be slow (10-30 seconds)
- Run full review manually or in CI

### 2. Make Hooks Informative

Provide clear error messages:
```bash
if [ $? -ne 0 ]; then
  echo ""
  echo "❌ Pre-commit checks failed!"
  echo ""
  echo "Issues found:"
  echo "  - Possible secrets in code"
  echo "  - console.log statements"
  echo ""
  echo "To fix:"
  echo "  1. Remove secrets (use environment variables)"
  echo "  2. Remove console.log statements"
  echo ""
  echo "To bypass (not recommended):"
  echo "  git commit --no-verify"
  exit 1
fi
```

### 3. Document for Your Team

Add to your project's README:
```markdown
## Development Workflow

This project uses pre-commit hooks for code quality:

- Secrets are automatically detected and blocked
- console.log statements are flagged
- debugger statements are blocked

To bypass (for WIP commits): `git commit --no-verify`
```

### 4. Combine with CI

```yaml
# .github/workflows/review.yml
name: Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate diff
        run: |
          python scripts/generate_diff.py origin/${{ github.base_ref }} HEAD
      
      - name: Run checks
        run: |
          scripts/check_critical.sh .review/diff.txt
```

---

## Examples

### Minimal Hook (Secrets Only)

```bash
#!/bin/bash
SKILL_DIR=".cursor/skills/review-before-pr"
$SKILL_DIR/scripts/generate_diff.sh --staged
grep -qE '(api[_-]?key|password|secret)' .review/diff.txt && echo "⚠️  Secrets detected!" && exit 1
exit 0
```

### Comprehensive Hook

```bash
#!/bin/bash
set -e

SKILL_DIR=".cursor/skills/review-before-pr"

echo "🔍 Running pre-commit checks..."

# Generate diff
$SKILL_DIR/scripts/generate_diff.sh --staged

# Run all automated checks
$SKILL_DIR/scripts/check_critical.sh .review/diff.txt

# Check test coverage
if git diff --cached --name-only | grep -qE '\.(ts|js)$'; then
  echo "📝 Code changes detected, checking for tests..."
  if ! git diff --cached --name-only | grep -qE '\.test\.(ts|js)$'; then
    echo "⚠️  Warning: Code changes without test changes"
  fi
fi

# Check for large files
if git diff --cached --stat | grep -qE '\|\s+[0-9]{3,}\s+\+'; then
  echo "⚠️  Warning: Large file changes detected (>100 lines)"
fi

echo "✅ All pre-commit checks passed"
exit 0
```

---

## Further Reading

- [Husky Documentation](https://typicode.github.io/husky/)
- [pre-commit Framework](https://pre-commit.com/)
- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)

---

For more help, see:
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Configuration Guide](CONFIGURATION.md)
- [README](../README.md)
