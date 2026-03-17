# Review Before PR Skill

**Review your code before you open a PR.** Get a structured, AI-powered code review (design, security, performance, tests) as a single markdown report—no GitHub, no API keys, no PR required. Works on any git repo, offline. Use it with **any AI agent** that supports skills (Cursor, Claude Code, Windsurf, Gemini, etc.).

---

## Why this exists

Most code-review tools assume you already have a pull request. This skill is for the step **before** that: you want feedback on your branch, your staged changes, or your local edits so you can fix issues and polish the diff *before* raising a PR. No GitHub dependency, no external services—just your repo and your AI agent.

**Use it when you:**

- Want a review of your branch vs `main` (or any base) before opening a PR
- Want to double-check what you're about to commit (`--staged`)
- Want feedback on all uncommitted work (`--local`)

You get one markdown file with **Critical**, **High**, **Medium**, and **Positive notes**, plus suggested code snippets *in the doc only*—your source files stay untouched unless you choose to apply changes.

---

## What makes it different


|                     | This skill                               | Typical PR review tools               |
| ------------------- | ---------------------------------------- | ------------------------------------- |
| **When**            | Before you open a PR                     | After you open a PR                   |
| **Needs GitHub?**   | No                                       | Yes (PR number, `gh` CLI, etc.)       |
| **Needs API keys?** | No                                       | Often (GitHub token, service account) |
| **Works offline?**  | Yes                                      | Usually no                            |
| **Modes**           | Branch vs branch, staged only, all local | PR-only                               |
| **Output**          | One markdown report (git-ignored)        | Inline comments on the PR             |


So: **review first, PR when you're ready.**

---

## Repository layout

```
review-before-pr/
├── README.md
├── SKILL.md
├── references/
│   └── REVIEW_CHECKLIST.md
└── scripts/
    └── generate_diff.sh
```

---

## Installation

Clone this repo **directly** into your AI agent's skills directory. From your **project root** (the repo you want to review), run the command for your agent.


| Agent           | Skills directory                          | Install command                                                                                |
| --------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Cursor**      | `.cursor/skills/review-before-pr`         | `git clone https://github.com/amanblog/review-before-pr.git .cursor/skills/review-before-pr`   |
| **Claude Code** | `.claude/skills/review-before-pr`         | `git clone https://github.com/amanblog/review-before-pr.git .claude/skills/review-before-pr`   |
| **Windsurf**    | `.windsurf/skills/review-before-pr`       | `git clone https://github.com/amanblog/review-before-pr.git .windsurf/skills/review-before-pr` |
| **Continue**    | `.continue/skills/review-before-pr`       | `git clone https://github.com/amanblog/review-before-pr.git .continue/skills/review-before-pr` |
| **Other**       | Check your agent's docs for "skills" path | Clone into that path as `review-before-pr`.                                                    |


Ensure your repo has `**.review/`** in `.gitignore` so diff and review output aren't committed. The script will add it automatically if missing.

---

## Usage

You can use the skill in three ways. How you *invoke* it depends on your AI agent (see [How agents invoke skills](#how-agents-invoke-skills) below).

### 1. Ask the agent to review your branch (recommended)

In chat, ask the agent to review your **current branch** against a base branch (e.g. `main` or `develop`) using this skill. The agent will run the diff script and then produce the review.

**Example prompts:**

- *"Review my current branch against `main` using the review-before-pr skill"*
- *"Review my branch against `develop` using review-before-pr"*
- *"Review my staged changes using the review-before-pr skill"*
- *"Review my local (uncommitted) changes using review-before-pr"*

The agent runs the script, writes the diff to `.review/diff.txt`, analyzes it, and writes the report to e.g. `.review/review-<branch>.md`.

### 2. Use a slash command or pick the skill (when your agent supports it)

In **Cursor**: type `**/*`* in Agent chat, then choose **review-before-pr** from the list (or type the skill name). When prompted, say which base branch to compare against (e.g. `main`, `develop`) or that you want staged/local changes.

In **Claude Code**: type `**/review-before-pr`**. In **Windsurf**: type `**@review-before-pr`** in Cascade. See the table below for other agents.

### 3. Run the diff yourself, then ask for a review

Generate the diff from the CLI (use the path where you **installed** the skill, e.g. `.cursor/skills/review-before-pr`), then ask the agent to review `.review/`:

```bash
# From project root — <SKILL_DIR> = where you installed the skill (e.g. .cursor/skills/review-before-pr)
<SKILL_DIR>/scripts/generate_diff.sh main my-feature-branch
# Or: --staged for staged only, --local for all local changes
```

Examples:

- **Cursor:** `.cursor/skills/review-before-pr/scripts/generate_diff.sh main my-branch`
- **Claude Code:** `.claude/skills/review-before-pr/scripts/generate_diff.sh main my-branch`

Then in chat: *"Review the diff in `.review/diff.txt` using the review-before-pr skill"*. The agent will read the diff and write the report under `.review/`.

---

### How agents invoke skills


| Agent           | How to invoke this skill                                                                                                                             |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cursor**      | Type `**/`** in Agent chat, then select **review-before-pr**. You can also type the skill name. [Cursor skills docs](https://cursor.com/docs/skills) |
| **Claude Code** | Type `**/review-before-pr`**. [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills)                                               |
| **Windsurf**    | Type `**@review-before-pr`** in Cascade. [Windsurf Cascade skills](https://docs.windsurf.com/windsurf/cascade/skills)                                |
| **Continue**    | Use natural language in Agent mode, e.g. *"Review my current branch against main using the review-before-pr skill"*.                                 |
| **Other**       | Check your agent's docs; invoke by name or via the UI.                                                                                               |


---

## What you get

The review document is organized into **Critical**, **High priority**, **Medium / good-to-have**, and **Positive notes**, with suggested fixes as code blocks in the doc. For very large diffs (e.g. 5,000+ lines), the agent summarizes by file/module.

**Example:** See [examples/sample-review.md](examples/sample-review.md) for a complete review output.

---

## ✨ New Features (v2.0)

### Smart Filtering
Automatically excludes noise files (lock files, SVGs, build artifacts) to keep reviews focused on actual code. Saves AI tokens and improves review quality.

### Secret Detection
Scans for hardcoded secrets (API keys, tokens, passwords) before generating diffs. Prevents accidental exposure to AI APIs.

### Cross-Platform Support
Works on Mac, Linux, and Windows. Python version available for full Windows compatibility.

### Configuration
Customize ignore patterns, secret detection, and review focus areas with `.reviewrc` file. See [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

### Context-Aware Reviews
AI proactively searches your codebase for related code, reducing false positives and improving accuracy.

### Metrics Tracking
Track code quality trends over time with automatic metrics logging.

---

## Configuration

Create a `.reviewrc` file in your project root to customize behavior:

```json
{
  "baseBranch": "develop",
  "ignorePatterns": ["*.generated.ts", "migrations/*"],
  "review": {
    "categories": ["security", "performance"],
    "contextGathering": true
  }
}
```

**Full documentation:** [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

---

## Advanced Features

### Safe Fix Application (Coming Soon)

After reviewing, apply suggested fixes safely via patch files:

```bash
# Generate patch for Critical fixes
python scripts/apply_fixes.py --priority critical --preview

# Review the patch, then apply
python scripts/apply_fixes.py --priority critical --apply

# Rollback if needed
git apply -R .review/patches/critical-fixes.patch
```

### Metrics Tracking

View your code quality trends:

```bash
python scripts/analyze_metrics.py
```

### Pre-commit Integration

Automatically review staged changes before committing. See [docs/PRECOMMIT_SETUP.md](docs/PRECOMMIT_SETUP.md).

---

## Troubleshooting

### Windows: "bash: command not found"

**Solution 1:** Install Git Bash (comes with Git for Windows)
```powershell
winget install Git.Git
```

**Solution 2:** Use Python version (works on all platforms)
```powershell
python .cursor/skills/review-before-pr/scripts/generate_diff.py --staged
```

### "Secret detected" error

If you need to review code containing test API keys:

```bash
# Temporarily disable secret detection
./scripts/generate_diff.sh --allow-secrets main feature
```

### Large diff timeout

For diffs >5000 lines, the AI will summarize. To review specific parts:

```bash
# Split into smaller reviews by directory
./scripts/generate_diff.sh main feature .review/frontend.txt -- src/frontend/
./scripts/generate_diff.sh main feature .review/backend.txt -- src/backend/
```

**Full troubleshooting guide:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Comparison with Other Tools

| Feature | review-before-pr | CodeRabbit | Qodo | GitHub Copilot | SonarQube |
|---------|------------------|------------|------|----------------|-----------|
| **Pre-PR reviews** | ✅ Core focus | ⚠️ Supports | ⚠️ Supports | ❌ PR-only | ⚠️ CI-only |
| **Local execution** | ✅ Yes | ⚠️ CLI only | ❌ No | ❌ No | ✅ Yes |
| **No API keys needed** | ✅ Yes | ❌ Requires account | ❌ Requires account | ❌ Requires license | ✅ Yes |
| **Works offline** | ✅ Yes | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **AI-powered** | ✅ Yes (your agent) | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Rules-based |
| **Context-aware** | ✅ Yes (v2.0) | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Limited |
| **Secret detection** | ✅ Yes (v2.0) | ✅ Yes | ⚠️ Limited | ❌ No | ✅ Yes |
| **Metrics tracking** | ✅ Yes (v2.0) | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Cost** | **Free** | $12-48/user/mo | $19-39/user/mo | $10-39/user/mo | Free (OSS) |

---

## Requirements

- A **git repository**
- An **AI agent that supports skills** (Cursor, Claude Code, Windsurf, Continue, etc.)
- **Python 3.7+** (for cross-platform support and secret detection)

---

## Documentation

- [Configuration Guide](docs/CONFIGURATION.md) - Customize for your project
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Pre-commit Setup](docs/PRECOMMIT_SETUP.md) - Automatic reviews before commits
- [Sample Review Output](examples/sample-review.md) - See what you'll get

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT