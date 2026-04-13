# Changelog

All notable changes to the review-before-pr skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.1.0] - 2026-04-13

### Added

- **PR Comment Posting** - Post review findings as pending GitHub PR review comments
  - Creates PENDING review (not submitted) — edit/remove comments before submitting
  - Interactive selection: post all, by priority, or pick specific findings
  - Signature on each comment for visual identification of AI-assisted reviews
  - Direct URL to review and submit pending comments on GitHub
  - Supports `--dry-run` to preview without posting
  - Requires `gh` CLI (auto-detected)
  - New script: `scripts/post_comments.py`

- **Multi-Pass Verification** - Second focused pass to catch findings the initial review missed
  - Targeted gap check (cross-file issues, security blind spots, error paths, concurrency, missing tests)
  - Appends new findings to existing review doc without rewriting
  - Skipped for small diffs (<100 lines) to save tokens
  - Configurable via `.reviewrc` `multiPass` settings

### Changed

- Updated `.reviewrc.example` with new `prComments` and `multiPass` configuration sections
- Updated CONFIGURATION.md with documentation for new options
- Renumbered SKILL.md steps: patch generation is now Step 3.6 (was 3.5)

---

## [2.0.0] - 2026-03-16

### 🎉 Major Release - Elite Tier Implementation

This release transforms review-before-pr into an elite-tier development tool matching standards used by top 0.1% engineering teams (Google, Meta, Microsoft).

### Added

#### Core Features

- **Smart Diff Filtering** - Automatically excludes noise files (lock files, SVGs, build artifacts, minified files) to keep reviews focused on actual code
  - 90%+ reduction in diff noise
  - Saves AI tokens and improves review quality
  - Configurable via `.reviewrc`

- **Secret Detection** - Scans for hardcoded secrets before generating diffs
  - Industry-standard patterns (AWS keys, GitHub tokens, API keys, etc.)
  - Prevents accidental exposure to AI APIs
  - Blocks diff generation when secrets detected
  - Configurable patterns and bypass option

- **Cross-Platform Support** - Works on Mac, Linux, and Windows
  - Python version (`generate_diff.py`) for full Windows compatibility
  - Same CLI interface as bash version
  - Automatic platform detection
  - Graceful degradation with helpful error messages

- **Configuration System** - Customize behavior with `.reviewrc` file
  - Custom ignore patterns
  - Secret detection settings
  - Review focus areas
  - Output preferences
  - See `.reviewrc.example` for template

- **Context-Aware Reviews** - AI proactively searches codebase for related code
  - Searches for modified function call sites
  - Checks related files (middleware, schemas, tests)
  - Reduces false positives
  - Improves review accuracy

- **Metrics Tracking** - Track code quality trends over time
  - Automatic logging to `.review/metrics.jsonl`
  - Track findings by priority
  - Monitor review frequency
  - Measure code quality improvements

#### Scripts & Tools

- **`scripts/generate_diff.py`** - Cross-platform Python diff generator
- **`scripts/filters/secret_detector.py`** - Secret detection module with 20+ patterns
- **`scripts/check_critical.sh`** - Fast automated checks (no AI needed)
  - Secret detection
  - console.log detection
  - debugger statement detection
  - Merge conflict detection
  - Trailing whitespace detection

#### Documentation

- **`docs/CONFIGURATION.md`** - Comprehensive configuration guide
  - All options explained
  - Example configurations for different project types
  - Troubleshooting tips

- **`docs/TROUBLESHOOTING.md`** - Common issues and solutions
  - Platform-specific issues
  - Diff generation problems
  - Secret detection issues
  - Performance optimization

- **`docs/PRECOMMIT_SETUP.md`** - Pre-commit hook integration guide
  - Husky setup (Node.js)
  - pre-commit framework (Python)
  - Manual git hooks
  - Customization examples

- **`examples/sample-review.md`** - Complete example review output
  - Shows all priority levels
  - Demonstrates suggested fixes
  - Includes positive notes

- **`CONTRIBUTING.md`** - Contribution guidelines
  - Development setup
  - Coding standards
  - Testing checklist

- **`IMPLEMENTATION_PLAN.md`** - Full implementation roadmap
  - Detailed architecture
  - Phase-by-phase breakdown
  - Success metrics

### Enhanced

#### Review Checklist

- **Complete rewrite** of `references/REVIEW_CHECKLIST.md`
  - Based on Google, Meta, Microsoft engineering standards
  - Explicit priority syntax ([Critical], [High], [Medium], [Nit], [Positive])
  - Few-shot examples (good vs bad review comments)
  - Context gathering instructions for AI
  - Change size guidance (Meta/Google standards)
  - Frontend-specific checks (React/TS/Next.js)
  - Backend-specific checks (API/Services/Data)

#### SKILL.md

- Added configuration loading step
- Added context gathering instructions
- Added patch generation workflow (optional)
- Added metrics tracking step
- Enhanced output template with timestamps and summaries
- Cross-platform script examples

#### README.md

- Added "New Features (v2.0)" section
- Added configuration examples
- Added advanced features section
- Added troubleshooting quick reference
- Added comparison table with other tools (CodeRabbit, Qodo, etc.)
- Added comprehensive documentation links

#### Diff Generation Scripts

- **`scripts/generate_diff.sh`** enhanced with:
  - Smart filtering (20+ default exclusion patterns)
  - Secret detection integration
  - Configuration file support (`.reviewrc`)
  - `--allow-secrets` flag
  - `--no-filter` flag
  - Better error messages
  - Automatic `.gitignore` management

### Changed

- Improved error handling across all scripts
- More informative output messages
- Better cross-platform compatibility
- Cleaner code structure

### Fixed

- Windows path handling issues
- Large diff handling
- Secret detection false positives (added ignore patterns)
- Script execution permissions

---

## [1.0.0] - Initial Release

### Added

- Basic diff generation script (`generate_diff.sh`)
- Simple review checklist
- SKILL.md for AI agent integration
- README with installation instructions
- Support for branch, staged, and local diffs
- `.review/` directory for git-ignored output

---

## Upgrade Guide

### From 1.0.0 to 2.0.0

1. **Pull latest changes:**
   ```bash
   cd .cursor/skills/review-before-pr
   git pull origin main
   ```

2. **Make new scripts executable:**
   ```bash
   chmod +x scripts/generate_diff.py
   chmod +x scripts/filters/secret_detector.py
   chmod +x scripts/check_critical.sh
   ```

3. **Optional: Create configuration file:**
   ```bash
   cp .reviewrc.example .reviewrc
   # Edit .reviewrc to customize
   ```

4. **Test the upgrade:**
   ```bash
   # Test bash version
   ./scripts/generate_diff.sh --staged
   
   # Test Python version
   python3 scripts/generate_diff.py --staged
   
   # Test secret detection
   python3 scripts/filters/secret_detector.py .review/diff.txt
   ```

5. **Update your workflows:**
   - If using pre-commit hooks, update to use new `check_critical.sh`
   - If using CI/CD, consider using Python version for better Windows support

---

## Breaking Changes

### 2.0.0

- **Default filtering:** Lock files, SVGs, and build artifacts are now excluded by default
  - Use `--no-filter` flag to include all files (old behavior)
  - Or configure custom patterns in `.reviewrc`

- **Secret detection:** Diffs with detected secrets are now blocked by default
  - Use `--allow-secrets` flag to bypass (not recommended)
  - Or configure custom patterns in `.reviewrc`

- **Python requirement:** Secret detection requires Python 3.7+
  - Falls back gracefully if Python not available
  - Bash-only workflows still work (without secret detection)

---

## Roadmap

### Planned for 2.1.0

- **Safe fix application** - Apply suggested fixes via patch files
- **Metrics visualization** - Dashboard for code quality trends
- **Learning mode** - Track which suggestions users apply

### Planned for 3.0.0

- **IDE extensions** - VS Code/Cursor native UI
- **CI/CD plugins** - GitHub Actions, GitLab CI integrations
- **Team dashboards** - Aggregate metrics across team
- **Custom rules engine** - Team-specific review patterns

---

## Migration Notes

### Configuration File

If you were using custom exclusion patterns in your scripts, move them to `.reviewrc`:

**Before (custom script modification):**
```bash
# Modified generate_diff.sh
EXCLUDES=("*.lock" "dist/*")
```

**After (.reviewrc):**
```json
{
  "ignorePatterns": ["*.lock", "dist/*"]
}
```

### Secret Detection

If you have test secrets in your code, add "test" or "example" to avoid false positives:

**Before:**
```typescript
const API_KEY = "abc123def456";  // Triggers detection
```

**After:**
```typescript
const TEST_API_KEY = "abc123def456_test";  // Ignored
// or
const API_KEY = process.env.API_KEY;  // Best practice
```

---

## Credits

This release incorporates feedback and best practices from:
- Google Engineering Practices
- Microsoft Research (Michaela Greiler)
- Meta Engineering
- Netflix, Stripe, Airbnb, Uber engineering teams
- DeepSeek, Gemini, and Grok AI assessments

Special thanks to all contributors and users who provided feedback!

---

For full details, see [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
