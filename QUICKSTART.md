# Quick Start Guide

Get up and running with review-before-pr in 5 minutes.

---

## 1. Install (30 seconds)

Choose your AI agent and run the install command from your **project root**:

```bash
# Cursor
git clone https://github.com/amanblog/review-before-pr.git .cursor/skills/review-before-pr

# Claude Code
git clone https://github.com/amanblog/review-before-pr.git .claude/skills/review-before-pr

# Windsurf
git clone https://github.com/amanblog/review-before-pr.git .windsurf/skills/review-before-pr
```

---

## 2. First Review (2 minutes)

### Option A: Ask your AI agent (easiest)

Just say:
```
"Review my current branch against main using the review-before-pr skill"
```

or

```
"Review my staged changes using review-before-pr"
```

### Option B: Run manually

```bash
# For Cursor users
.cursor/skills/review-before-pr/scripts/generate_diff.sh --staged

# Then ask AI: "Review .review/diff.txt"
```

---

## 3. Check the Output

Open `.review/review-<branch>.md` to see your review with:

- **Critical** issues (must fix)
- **High priority** issues (should fix)
- **Medium** suggestions (good to have)
- **Positive** notes (what you did well!)

---

## 4. Optional: Configure (2 minutes)

Create `.reviewrc` in your project root:

```bash
cp .cursor/skills/review-before-pr/.reviewrc.example .reviewrc
```

Edit to customize:

```json
{
  "baseBranch": "develop",
  "ignorePatterns": ["*.generated.ts", "migrations/*"],
  "review": {
    "categories": ["security", "performance"]
  }
}
```

---

## 5. Optional: Pre-commit Hook (1 minute)

Automatically check before commits:

```bash
# For Node.js projects with Husky
npm install --save-dev husky
npx husky init

cat > .husky/pre-commit << 'EOF'
#!/bin/sh
.cursor/skills/review-before-pr/scripts/generate_diff.sh --staged
.cursor/skills/review-before-pr/scripts/check_critical.sh .review/diff.txt
EOF

chmod +x .husky/pre-commit
```

---

## Common Commands

```bash
# Review current branch vs main
./scripts/generate_diff.sh main $(git branch --show-current)

# Review staged changes
./scripts/generate_diff.sh --staged

# Review all local changes
./scripts/generate_diff.sh --local

# Skip secret detection (not recommended)
./scripts/generate_diff.sh --allow-secrets --staged

# Include all files (no filtering)
./scripts/generate_diff.sh --no-filter --staged
```

---

## Windows Users

Use the Python version:

```powershell
# Install Git for Windows (includes Git Bash)
winget install Git.Git

# Or use Python version directly
python .cursor/skills/review-before-pr/scripts/generate_diff.py --staged
```

---

## Troubleshooting

### "bash: command not found"
- **Mac/Linux:** Make scripts executable: `chmod +x scripts/*.sh`
- **Windows:** Use Python version or install Git Bash

### "Secret detected"
- Remove secrets from code (use environment variables)
- Or bypass temporarily: `--allow-secrets` flag

### "No changes"
- For `--staged`: Run `git add` first
- For branch diff: Make sure branches exist

---

## Next Steps

- **Read the full docs:** [README.md](README.md)
- **Configure for your project:** [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- **Set up pre-commit hooks:** [docs/PRECOMMIT_SETUP.md](docs/PRECOMMIT_SETUP.md)
- **See example output:** [examples/sample-review.md](examples/sample-review.md)

---

## Getting Help

- **Troubleshooting:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **GitHub Issues:** https://github.com/amanblog/review-before-pr/issues
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

**That's it! You're ready to get elite-level code reviews before every PR.** 🚀
