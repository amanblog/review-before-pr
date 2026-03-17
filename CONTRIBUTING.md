# Contributing to review-before-pr

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

---

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

---

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** (if available)
3. **Include:**
   - Your OS and version
   - AI agent and version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs

### Suggesting Features

1. **Check existing issues** for similar requests
2. **Describe the use case** - why is this needed?
3. **Provide examples** of how it would work
4. **Consider alternatives** you've explored

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly** on multiple platforms (Mac, Linux, Windows if possible)
5. **Update documentation** if needed
6. **Commit with clear messages**
7. **Push and create a PR**

---

## Development Setup

### Prerequisites

- Git
- Bash (Mac/Linux) or Git Bash (Windows)
- Python 3.7+
- An AI agent that supports skills (Cursor, Claude Code, etc.)

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/review-before-pr.git
cd review-before-pr

# Install in your AI agent's skills directory for testing
# For Cursor:
ln -s $(pwd) ~/.cursor/skills/review-before-pr

# Make scripts executable
chmod +x scripts/*.sh scripts/*.py scripts/filters/*.py
```

### Testing Your Changes

1. **Test bash script:**
   ```bash
   ./scripts/generate_diff.sh --staged
   ```

2. **Test Python script:**
   ```bash
   python3 scripts/generate_diff.py --staged
   ```

3. **Test secret detection:**
   ```bash
   # Create a test diff with a fake secret
   echo '+ const API_KEY = "AKIAIOSFODNN7EXAMPLE"' > .review/test.txt
   python3 scripts/filters/secret_detector.py .review/test.txt
   ```

4. **Test automated checks:**
   ```bash
   ./scripts/check_critical.sh .review/diff.txt
   ```

5. **Test with your AI agent:**
   - Ask: "Review my staged changes using review-before-pr"
   - Verify the review output

---

## Project Structure

```
review-before-pr/
├── SKILL.md                      # Main skill definition (AI agent reads this)
├── README.md                     # User-facing documentation
├── IMPLEMENTATION_PLAN.md        # Development roadmap
├── references/
│   └── REVIEW_CHECKLIST.md      # Review guidelines (Google/Meta/Microsoft standards)
├── scripts/
│   ├── generate_diff.sh         # Bash diff generator (Mac/Linux)
│   ├── generate_diff.py         # Python diff generator (cross-platform)
│   ├── check_critical.sh        # Automated checks
│   └── filters/
│       └── secret_detector.py   # Secret detection module
├── docs/
│   ├── CONFIGURATION.md         # Configuration guide
│   ├── TROUBLESHOOTING.md       # Common issues
│   └── PRECOMMIT_SETUP.md       # Pre-commit hook setup
└── examples/
    └── sample-review.md         # Example review output
```

---

## Coding Standards

### Bash Scripts

- Use `#!/usr/bin/env bash` shebang
- Include `set -e` for error handling
- Add comments for complex logic
- Provide usage examples in header
- Use meaningful variable names
- Quote variables: `"$VAR"` not `$VAR`

### Python Scripts

- Use `#!/usr/bin/env python3` shebang
- Follow PEP 8 style guide
- Add docstrings for functions and classes
- Use type hints where appropriate
- Handle errors gracefully
- No external dependencies (use stdlib only)

### Documentation

- Use clear, concise language
- Include code examples
- Provide troubleshooting tips
- Keep formatting consistent
- Update table of contents if needed

---

## Commit Message Guidelines

Use conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(filters): add support for custom secret patterns

Allow users to define custom secret detection patterns in .reviewrc
configuration file.

Closes #123
```

```
fix(windows): handle paths with spaces in Python script

Windows paths with spaces were causing script failures. Now properly
quote all path arguments.

Fixes #456
```

---

## Testing Checklist

Before submitting a PR, verify:

- [ ] Code works on Mac/Linux
- [ ] Code works on Windows (if applicable)
- [ ] Python script works with Python 3.7+
- [ ] Bash script works with Bash 3.2+ (macOS default)
- [ ] No external dependencies added (unless discussed)
- [ ] Documentation updated
- [ ] Examples updated if behavior changed
- [ ] No secrets or sensitive data in commits
- [ ] Scripts are executable (`chmod +x`)
- [ ] Error messages are helpful
- [ ] Edge cases handled

---

## Areas for Contribution

### High Priority

- **Cross-platform testing:** Test on Windows, various Linux distros
- **AI agent compatibility:** Test with different AI agents
- **Performance optimization:** Make diff generation faster
- **Secret detection patterns:** Add more secret types

### Medium Priority

- **Metrics visualization:** Create dashboard for metrics
- **IDE integration:** VS Code extension for inline reviews
- **CI/CD examples:** GitHub Actions, GitLab CI templates
- **Patch application:** Implement safe fix application system

### Low Priority

- **Internationalization:** Support for non-English languages
- **Custom review rules:** Team-specific rule engine
- **Learning mode:** Track which suggestions users apply

---

## Questions?

- **General questions:** Open a discussion on GitHub
- **Bug reports:** Open an issue
- **Feature requests:** Open an issue with [Feature Request] prefix
- **Security issues:** Email maintainer directly (see README)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
