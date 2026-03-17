# Troubleshooting Guide

Common issues and solutions for the review-before-pr skill.

---

## Installation Issues

### Skill not found by AI agent

**Symptoms:**
- Agent says "skill not found" or doesn't recognize `/review-before-pr`
- Skill doesn't appear in skill picker

**Solutions:**

1. **Verify installation path:**
   ```bash
   # For Cursor
   ls -la .cursor/skills/review-before-pr
   
   # For Claude Code
   ls -la .claude/skills/review-before-pr
   
   # For Windsurf
   ls -la .windsurf/skills/review-before-pr
   ```

2. **Check SKILL.md exists:**
   ```bash
   cat .cursor/skills/review-before-pr/SKILL.md
   ```

3. **Restart your AI agent** after installation

4. **Try explicit invocation:**
   - Instead of `/review-before-pr`, say: "Review my current branch against main using the review-before-pr skill"

---

## Platform-Specific Issues

### Windows: "bash: command not found"

**Symptoms:**
- Error when running `generate_diff.sh`
- Script fails to execute on Windows

**Solutions:**

**Option 1: Use Python version (recommended)**
```powershell
python .cursor/skills/review-before-pr/scripts/generate_diff.py --staged
```

**Option 2: Install Git Bash**
```powershell
# Using winget
winget install Git.Git

# Or download from: https://git-scm.com/download/win
```

**Option 3: Use WSL (Windows Subsystem for Linux)**
```powershell
wsl --install
# Then run bash scripts inside WSL
```

**Option 4: Ask agent to use Python version**
- Say: "Use the Python version of the diff generator"
- Agent will automatically use `generate_diff.py` instead

---

### macOS: Permission denied

**Symptoms:**
- `Permission denied` when running scripts
- Scripts won't execute

**Solution:**
```bash
# Make scripts executable
chmod +x .cursor/skills/review-before-pr/scripts/generate_diff.sh
chmod +x .cursor/skills/review-before-pr/scripts/generate_diff.py
chmod +x .cursor/skills/review-before-pr/scripts/filters/secret_detector.py
```

---

## Diff Generation Issues

### "Not inside a git repository"

**Symptoms:**
- Error: "not inside a git repository"
- Script fails immediately

**Solutions:**

1. **Verify you're in a git repo:**
   ```bash
   git status
   ```

2. **Initialize git if needed:**
   ```bash
   git init
   ```

3. **Check you're in project root:**
   ```bash
   pwd
   # Should show your project directory
   ```

---

### "No changes" but files were modified

**Symptoms:**
- Script says "No changes" but you know files changed
- Empty diff file

**Solutions:**

1. **Check what mode you're using:**
   - `--staged`: Only shows staged changes (use `git add` first)
   - `--local`: Shows all uncommitted changes
   - `branch vs branch`: Only shows committed changes

2. **Verify changes exist:**
   ```bash
   # Check staged changes
   git diff --cached
   
   # Check local changes
   git diff HEAD
   
   # Check branch diff
   git diff main..your-branch
   ```

3. **Check if files are filtered:**
   - Lock files, SVGs, and build outputs are excluded by default
   - Use `--no-filter` to include all files:
     ```bash
     ./scripts/generate_diff.sh --no-filter --staged
     ```

---

### Large diff timeout

**Symptoms:**
- Review takes very long or times out
- AI says diff is too large

**Solutions:**

1. **Split review by directory:**
   ```bash
   # Review frontend separately
   ./scripts/generate_diff.sh main feature .review/frontend.txt -- src/frontend/
   
   # Review backend separately
   ./scripts/generate_diff.sh main feature .review/backend.txt -- src/backend/
   ```

2. **Review in chunks:**
   - Review critical files first
   - Then review remaining files

3. **Use staged reviews:**
   - Stage files in batches
   - Review each batch with `--staged`

4. **Increase context window:**
   - Some AI agents support larger context windows
   - Check your agent's settings

---

## Secret Detection Issues

### "Secret detected" error (false positive)

**Symptoms:**
- Script blocks with "Secrets detected!"
- But the "secrets" are test data or examples

**Solutions:**

1. **Add "test" or "example" to the string:**
   ```typescript
   // Before (triggers detection)
   const API_KEY = "abc123def456";
   
   // After (ignored)
   const TEST_API_KEY = "abc123def456_test";
   ```

2. **Use environment variables:**
   ```typescript
   // Instead of hardcoding
   const API_KEY = process.env.API_KEY;
   ```

3. **Temporarily bypass (not recommended):**
   ```bash
   ./scripts/generate_diff.sh --allow-secrets main feature
   ```

4. **Configure custom patterns:**
   - Edit `.reviewrc` to exclude specific patterns
   - See [CONFIGURATION.md](CONFIGURATION.md) for details

---

### Real secrets not detected

**Symptoms:**
- Actual secrets pass through detection
- No warning when there should be

**Solutions:**

1. **Check Python is installed:**
   ```bash
   python3 --version
   # or
   python --version
   ```

2. **Verify secret detector exists:**
   ```bash
   ls -la scripts/filters/secret_detector.py
   ```

3. **Test secret detector manually:**
   ```bash
   python3 scripts/filters/secret_detector.py .review/diff.txt
   ```

4. **Add custom patterns:**
   - Edit `.reviewrc` to add your secret patterns
   - See [CONFIGURATION.md](CONFIGURATION.md#security-options)

---

## Configuration Issues

### Configuration not loading

**Symptoms:**
- Custom ignore patterns not applied
- Settings in `.reviewrc` ignored

**Solutions:**

1. **Check file location:**
   ```bash
   # Must be in project root
   ls -la .reviewrc
   ```

2. **Validate JSON syntax:**
   ```bash
   # Using Python
   python3 -m json.tool .reviewrc
   
   # Or use online validator: jsonlint.com
   ```

3. **Check for typos:**
   - Field names are case-sensitive
   - Use exact names from [CONFIGURATION.md](CONFIGURATION.md)

4. **Look for error messages:**
   - Script prints warnings for invalid config
   - Check stderr output

---

### Patterns not working

**Symptoms:**
- Files still appear in diff despite ignore patterns
- Exclusions don't take effect
- **package-lock.json or other lock files appear** when they should be excluded

**Solutions:**

1. **Pathspec parsing (lock files still in diff):**  
   Git can misparse `:!` pathspecs when patterns contain certain characters (e.g. `__pycache__`). The bundled scripts use `:(exclude)` instead of `:!` to avoid this. If you see default-excluded files (like `package-lock.json`) in the diff, ensure you're using the latest `generate_diff.sh` / `generate_diff.py` from the skill (they use `:(exclude)` throughout).

2. **Test glob patterns:**
   ```bash
   # See what files match your pattern
   git ls-files | grep "your-pattern"
   ```

2. **Use correct syntax:**
   ```json
   // Correct
   "ignorePatterns": ["*.lock", "dist/*"]
   
   // Wrong
   "ignorePatterns": [".lock", "/dist/"]
   ```

3. **Remember patterns are relative to repo root:**
   ```json
   // To exclude src/generated/
   "ignorePatterns": ["src/generated/**"]
   ```

4. **Use git pathspec for complex patterns (prefer `:(exclude)` over `:!`):**
   ```json
   "additionalExcludes": [":(exclude)**/test-fixtures/**"]
   ```

---

## Review Quality Issues

### AI missing obvious issues

**Symptoms:**
- Review doesn't catch clear bugs
- Important issues not flagged

**Solutions:**

1. **Check diff size:**
   - Very large diffs (>5000 lines) are summarized
   - Split into smaller reviews

2. **Enable context gathering:**
   ```json
   {
     "review": {
       "contextGathering": true
     }
   }
   ```

3. **Provide more context:**
   - Say: "Focus on security issues in auth.ts"
   - Or: "Check for race conditions"

4. **Use specific categories:**
   ```json
   {
     "review": {
       "categories": ["security", "correctness"]
     }
   }
   ```

---

### Too many nitpicky comments

**Symptoms:**
- Review has many style suggestions
- Overwhelming number of minor issues

**Solutions:**

1. **The checklist already filters nits:**
   - AI is instructed to skip style issues
   - Focus is on code health

2. **If still too many:**
   - Say: "Focus only on Critical and High priority issues"
   - Or: "Skip style and formatting comments"

3. **Run linter first:**
   ```bash
   # Fix style issues before review
   npm run lint --fix
   # or
   prettier --write .
   ```

---

### False positives

**Symptoms:**
- AI flags issues that aren't actually problems
- Suggests fixes for correct code

**Solutions:**

1. **Provide context:**
   - Say: "This is handled in middleware.ts"
   - Or: "This pattern is intentional for performance"

2. **Enable context gathering:**
   - AI will search for related code
   - Reduces false positives

3. **Report patterns:**
   - If specific false positives recur, add to `.reviewrc`
   - Or create `TEAM_REVIEW_RULES.md` with your patterns

---

## Performance Issues

### Slow diff generation

**Symptoms:**
- Script takes a long time to run
- Hangs or times out

**Solutions:**

1. **Check repo size:**
   ```bash
   # Count files
   git ls-files | wc -l
   
   # Check for large files
   git ls-files | xargs ls -lh | sort -k5 -h | tail -20
   ```

2. **Use more aggressive filtering:**
   ```json
   {
     "ignorePatterns": [
       "**/*.snap",
       "test-fixtures/**",
       "public/**"
     ]
   }
   ```

3. **Review specific paths:**
   ```bash
   # Only review src/
   ./scripts/generate_diff.sh main feature .review/diff.txt -- src/
   ```

---

### Slow AI review

**Symptoms:**
- Diff generates quickly but review is slow
- AI takes minutes to respond

**Solutions:**

1. **Reduce diff size:**
   - Split into smaller reviews
   - Review critical files first

2. **Disable context gathering temporarily:**
   ```json
   {
     "review": {
       "contextGathering": false
     }
   }
   ```

3. **Use faster AI model:**
   - Check your agent's model settings
   - Some agents offer faster models for reviews

---

## Integration Issues

### Pre-commit hook not working

**Symptoms:**
- Hook doesn't run on commit
- No review performed

**Solutions:**

1. **Check hook is executable:**
   ```bash
   chmod +x .husky/pre-commit
   # or
   chmod +x .git/hooks/pre-commit
   ```

2. **Verify hook path:**
   ```bash
   # Hook should reference correct skill path
   cat .husky/pre-commit
   ```

3. **Test hook manually:**
   ```bash
   .husky/pre-commit
   # or
   .git/hooks/pre-commit
   ```

4. **Check for errors:**
   - Look at hook output
   - Verify script paths are correct

---

### CI/CD integration fails

**Symptoms:**
- Review works locally but fails in CI
- Pipeline errors

**Solutions:**

1. **Check Python/Bash availability:**
   ```yaml
   # In CI config
   - name: Install dependencies
     run: |
       python3 --version
       git --version
   ```

2. **Use Python version in CI:**
   ```yaml
   - name: Generate diff
     run: python3 scripts/generate_diff.py --staged
   ```

3. **Set environment variables:**
   ```yaml
   env:
     REVIEW_ALLOW_SECRETS: "true"  # If needed
   ```

---

## Getting Help

### Still having issues?

1. **Check the logs:**
   - Look for error messages in terminal
   - Check `.review/security-warnings.txt` if it exists

2. **Try with minimal config:**
   - Remove `.reviewrc` temporarily
   - Test with default settings

3. **Verify installation:**
   ```bash
   # Check all files exist
   ls -R .cursor/skills/review-before-pr/
   ```

4. **Update the skill:**
   ```bash
   cd .cursor/skills/review-before-pr
   git pull origin main
   ```

5. **Open an issue:**
   - Go to: https://github.com/amanblog/review-before-pr/issues
   - Include:
     - Your OS and version
     - AI agent and version
     - Error messages
     - Steps to reproduce

---

## Common Error Messages

### "Error: base branch 'X' not found"

**Cause:** Branch doesn't exist in your repo

**Fix:**
```bash
# List all branches
git branch -a

# Use correct branch name
./scripts/generate_diff.sh main your-branch  # not 'master' if it doesn't exist
```

---

### "jq: command not found"

**Cause:** Optional JSON parser not installed (not critical)

**Fix:**
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# Or ignore - basic config parsing works without jq
```

---

### "ModuleNotFoundError: No module named 'X'"

**Cause:** Python dependencies missing (shouldn't happen - no deps required)

**Fix:**
```bash
# Verify Python version
python3 --version  # Should be 3.7+

# Script has no external dependencies
# If error persists, check Python installation
```

---

## Debug Mode

Enable verbose output for troubleshooting:

```bash
# Bash version
set -x
./scripts/generate_diff.sh --staged
set +x

# Python version
python3 -v scripts/generate_diff.py --staged
```

---

## Best Practices to Avoid Issues

1. **Keep diffs small:** < 500 lines ideal
2. **Run linter first:** Fix style before review
3. **Stage incrementally:** Review as you go
4. **Use configuration:** Customize for your project
5. **Update regularly:** Pull latest skill updates
6. **Test locally:** Before CI/CD integration

---

For more help, see:
- [Configuration Guide](CONFIGURATION.md)
- [README](../README.md)
- [GitHub Issues](https://github.com/amanblog/review-before-pr/issues)
