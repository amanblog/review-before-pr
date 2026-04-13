---
name: review-before-pr
description: Review code before opening a PR—generate a full diff and produce a structured markdown report (bugs, security, performance, suggested code in-doc only), with optional posting of findings as pending PR review comments on GitHub. Use when the user wants to review changes before opening a PR, "review my branch", "review my staged changes", or get a code review.
---

# Review Before PR

Review changes between two git branches and produce a **single markdown document** with findings and **suggested code snippets inside the doc** (do not apply changes to source files unless the user explicitly asks). Usable for any repo when there is no GitHub PR bot or AI review agent.

## When to Use

- User asks to **review their current branch against a base branch** (e.g. "review my branch against main/develop using the review-before-pr skill") — run the diff script with that base and current branch, then analyze and write the report.
- User asks to **review staged or local changes** (e.g. "review my staged changes" / "review my uncommitted changes") — run the script with `--staged` or `--local`, then analyze and write the report.
- User invokes this skill via **slash command or skill picker** (e.g. `/review-before-pr` in Cursor/Claude, `@review-before-pr` in Windsurf) — prompt for base branch or mode (staged/local) if not clear, then run the script and produce the review.
- User **already has a diff** in `.review/diff.txt` (or points to it) and asks to review it — skip running the script; read the diff and produce the review doc.
- User wants a structured code review with critical/high/medium findings and suggested code in the doc only (no edits to source unless they ask).

## Workflow

### Step 1: Get the full diff (no pager)

If the user has not already created a diff file, run the bundled script from the **project root**. The script lives at **`scripts/generate_diff.sh`** relative to this skill's directory—the full path depends on where the skill is installed (e.g. `.cursor/skills/review-before-pr`, `.claude/skills/review-before-pr`). When the user says "review my current branch against &lt;base&gt;", use the current branch as the feature branch (e.g. `git branch --show-current`). Output is written to **`.review/diff.txt`** by default (the `.review/` directory is in `.gitignore`, so the diff is not tracked by git).

```bash
# Committed changes only (branch vs branch) — default output: .review/diff.txt
bash "<skill-dir>/scripts/generate_diff.sh" <base-branch> <feature-branch>

# Staged changes only (what's in the index vs HEAD)
bash "<skill-dir>/scripts/generate_diff.sh" --staged

# All local changes (staged + unstaged vs HEAD)
bash "<skill-dir>/scripts/generate_diff.sh" --local

# Custom output path (e.g. for review doc later)
bash "<skill-dir>/scripts/generate_diff.sh" develop my-branch .review/my-pr.txt
```

Replace `<skill-dir>` with the actual path to this skill on the user's system (see the skill's README for per-agent install paths).

Or manually (output will be tracked unless you write to `.review/` or another ignored path, and note this does **not** apply the same ignore/secret rules as `generate_diff.sh`):

```bash
git --no-pager diff <base-branch>..<feature-branch> > .review/diff.txt
```

- **Branch vs branch**: only **committed** changes between the two refs.
- **`--staged`**: only **staged** changes (vs HEAD).
- **`--local`**: **staged + unstaged** (all local changes vs HEAD).
- Default path: `.review/diff.txt` (git-ignored). Use that path when attaching or referring to the diff.

If the user already provided a diff (pasted or attached), skip to Step 2.

### Step 1.5: Load Configuration (NEW)

Before analyzing, check for a `.reviewrc` configuration file in the project root:

```bash
# Check if config exists
if [ -f .reviewrc ]; then
  # Config is already loaded by the diff script
  # Review settings are available for customization
fi
```

The configuration file allows users to:
- Customize ignore patterns
- Enable/disable secret detection
- Set review categories
- Configure output format
- Control metrics tracking

### Step 2: Analyze the diff

First, read the checklist at **`references/REVIEW_CHECKLIST.md`** (relative to this skill's directory) to load the review categories. This checklist follows Google, Meta, and Microsoft engineering standards with explicit priority syntax and few-shot examples.

Then review the diff using the applicable sections (frontend, backend, or general as appropriate for the repo). Focus on:

- **Design** — Do the changes fit the codebase? Do they integrate well with the rest of the system? Is complexity justified? ([Google eng-practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html))
- **Functionality** — Does the code do what was intended? Edge cases, concurrency/races, and off-by-one or wrong conditions.
- **Security** — No secrets in code; input validated/sanitized; auth/authz respected; no XSS/injection vectors.
- **Complexity** — Code as simple as needed; no over-engineering for hypothetical future needs.
- **Tests** — Adequate tests for the change; tests are correct and maintainable.
- **Naming & comments** — Clear names; comments explain *why* where needed, not *what*.
- **Style & consistency** — Matches existing patterns and style guide; no unrelated style churn in the same change.
- **Documentation** — If behavior or APIs change, docs updated.
- **Context** — Consider the full file and system; flag if the change degrades overall code health.

For **frontend** repos, also consider: semantic HTML, CSS practices, JS/React patterns (hooks, keys, async cleanup), accessibility, i18n, and bundle/performance. For **backend**, consider: idempotency, transactions, input validation, error mapping, and logging. Use the checklist in `references/REVIEW_CHECKLIST.md` (same skill directory) for the relevant stack.

**Large diffs (5,000+ lines):** Summarize findings by file or module rather than reviewing line-by-line. Prioritize critical and high-priority items; group medium-priority items by theme. Note in the review doc that a full line-by-line review was not feasible due to diff size.

### Step 2.5: Context Gathering (NEW)

After reading the diff but before finalizing your analysis, proactively gather context:

1. **Identify modified exports**: Search for changed function/type signatures
   ```
   Example: If diff shows "export function getUser(id: string, includeDeleted: boolean)"
   Action: Search codebase for "getUser(" to find all call sites
   Check: Do they pass the new boolean parameter?
   ```

2. **Find call sites**: Use grep/search to find where modified functions are used
   ```bash
   # Search for function usage
   grep -r "functionName(" --include="*.ts" --include="*.tsx"
   ```

3. **Check related files**: Read middleware, schemas, tests related to changes
   ```
   Example: If auth.ts changes, read:
   - src/middleware/auth.ts (likely uses these functions)
   - src/auth/__tests__/auth.test.ts (test coverage)
   ```

4. **Gather architecture context**: Understand the broader system
   - If database models change, check for migrations
   - If API endpoints change, verify client code compatibility
   - If types change, check for breaking changes in dependents

This prevents "missing context" errors where you flag issues that are actually handled elsewhere in the codebase.

### Step 3: Produce the review document

Create **one markdown file**. By default write it under **`.review/`** so it is git-ignored but still openable in the editor (e.g. `.review/review-<branch-name>.md`). If the user asks for a different path (e.g. `docs/`), use that. Structure:

1. **Critical** — Bugs, security issues, data loss, broken user flows. Each item: file (and location if helpful), issue, and **suggested code block** in the doc only.
2. **High priority** — Logic errors, important edge cases, notable performance issues. Same: issue + **suggested code in the doc** where it helps.
3. **Medium / good-to-have** — Refactors, consistency, DX. Brief description; code snippets only when they clarify.
4. **Positive notes** — What was done well (good design, clear naming, solid tests). ([Google: "Good Things"](https://google.github.io/eng-practices/review/reviewer/looking-for.html#good-things))

**Rules for suggested code:**

- All suggested fixes go **inside the markdown document** as fenced code blocks.
- Do **not** edit the user's source files unless they explicitly ask you to apply a fix.
- Each finding: **File**, **Issue**, and **Suggested change** (code snippet in the doc).

### Step 3.5: Verification Pass (Multi-pass Review)

After producing the initial review document, do a **focused second pass** to catch findings that the first pass may have missed. This is not a full re-review — it is a targeted gap check that uses significantly fewer tokens.

**How to run the verification pass:**

1. Re-read the **Summary** section of your review document (not the full diff again).
2. Re-scan the diff with these specific lenses, checking **only** for things not already covered:
   - **Cross-file issues**: Are there patterns or inconsistencies *across* files that individual-file review missed? (e.g., an API contract changed in one file but callers in another file weren't updated)
   - **Security blind spots**: Any input validation, auth checks, or injection vectors missed?
   - **Error paths**: Are there unhappy paths (network failures, null/empty inputs, timeouts) not handled?
   - **Concurrency & state**: Race conditions, shared mutable state, missing locks?
   - **Missing tests**: Are there new code paths with no corresponding test coverage?
3. If the second pass finds new issues, **append them to the existing review document** under their appropriate priority section (do not rewrite findings from pass 1). Add a note like:

   ```markdown
   > *Found in verification pass*
   ```

4. Update the **Summary** section with revised counts if new findings were added.

**Token efficiency:** The second pass only re-reads the diff once with the targeted lenses above — it does **not** redo the full analysis. If the diff is large (5,000+ lines), the second pass should focus only on Critical and High priority categories.

**When to skip:** If the diff is small (<100 lines) and straightforward (e.g., a config change or documentation update), you may skip the verification pass.

### Step 3.6: Generate Patch File (Optional)

If the user says "apply fix #2" or "generate patch for security fixes":

1. Extract the suggested code from the review doc
2. Create a unified diff patch: `.review/patches/fixes-<timestamp>.patch`
3. Show patch preview to user:
   ```bash
   git apply --stat .review/patches/fixes-<timestamp>.patch
   ```
4. Ask for confirmation before applying
5. Apply with: `git apply .review/patches/fixes-<timestamp>.patch`
6. Provide rollback command: `git apply -R .review/patches/fixes-<timestamp>.patch`

**Safety rules:**
- NEVER auto-apply without user confirmation
- One fix at a time (or one category like "all Critical")
- Always generate patch first, apply second
- Provide rollback command

### Step 4: Track Metrics (NEW)

After generating the review, append to `.review/metrics.jsonl`:

```json
{"timestamp": "2026-03-16T10:30:00Z", "branch": "feature-auth", "mode": "branch", "base": "main", "diff_lines": 342, "files_changed": 12, "findings": {"critical": 2, "high": 5, "medium": 8, "positive": 3}, "secrets_detected": 0, "duration_seconds": 45}
```

This allows users to track review patterns over time and measure code quality improvements.

### Step 5: Post Comments to PR (Optional)

After the review document is generated, check if the current branch has an open PR. If it does (or the user provided a PR number), offer to post review findings as **pending review comments** directly on the PR.

**How this works:**

1. **Detect PR:** Run `gh pr view --json number,url` to check for an open PR on the current branch. If none found, skip this step silently (this step is only for PR-based reviews, not local/staged changes).

2. **Confirm with user:** Ask the user:
   ```
   PR #<number> detected. Would you like to post review comments to this PR?
   Options: all / select / skip
   ```
   - **all** — post all findings as pending comments
   - **select** — show numbered list, let user pick which findings to post (by number, priority level, or comma-separated list)
   - **skip** — don't post, just keep the review document

3. **Run the commenting script:**
   ```bash
   # Post all findings
   python3 "<skill-dir>/scripts/post_comments.py" .review/review-<branch>.md --all

   # Interactive selection (default)
   python3 "<skill-dir>/scripts/post_comments.py" .review/review-<branch>.md

   # Only critical + high priority
   python3 "<skill-dir>/scripts/post_comments.py" .review/review-<branch>.md --priority high

   # Specific PR number (if auto-detect fails)
   python3 "<skill-dir>/scripts/post_comments.py" .review/review-<branch>.md --pr 42

   # Preview without posting
   python3 "<skill-dir>/scripts/post_comments.py" .review/review-<branch>.md --dry-run
   ```

4. **Result:** The script creates a **PENDING** review on the PR. Comments are **not submitted** — they sit in the user's pending review state on GitHub, just like manually added review comments. The user can:
   - Edit comment text
   - Remove comments they don't want
   - Submit the review when ready

5. **Provide URL:** After posting, show the user the direct link to review and submit:
   ```
   ✅ Pending review created with N comment(s)!
   👉 Review and submit here: https://github.com/<owner>/<repo>/pull/<number>/files
   ```

**Signature:** Each comment includes a small footer identifying it as AI-assisted:
```
---
🔍 *Posted by review-before-pr — AI-assisted review · verify before submitting*
```

**Requirements:**
- `gh` CLI must be installed and authenticated (`gh auth status`)
- Current repo must have a GitHub remote
- A PR must exist for the current branch (or `--pr` flag used)

**When to skip:** If the user only asked for staged/local changes review, or if `gh` is not available, skip this step entirely. Only offer PR commenting when reviewing branch-vs-branch changes with an open PR.

## Output template

Use this structure in the generated review doc (follow the priority syntax from the checklist):

```markdown
# Code review: <feature-branch> vs <base-branch>

**Generated:** YYYY-MM-DD HH:MM:SS  
**Diff size:** X lines across Y files  
**Duration:** Z seconds

---

## Critical

### 1. Brief description

**File:** `path/to/file.ext:line_number`

**Issue:** Clear explanation of the problem and its impact.

**Suggested fix:**
```lang
// Exact code to replace or add
// Must be copy-paste ready
```

**Why this matters:** Brief context on business/technical impact.

---

## High priority
…

## Medium / good-to-have
…

## Positive notes

✅ **Category** - What was done well

…

---

## Summary

**Total findings:** X (Y Critical, Z High, W Medium)  
**Positive notes:** N

**Recommendation:** Fix the Critical issues before merging. High priority items should also be addressed.

**Overall:** This change [improves/maintains/degrades] code health by [explanation].
```

## Quick start

1. **User asks to review branch vs base:** Run `<skill-dir>/scripts/generate_diff.sh <base-branch> <feature-branch>` from project root (use current branch as feature-branch), then analyze `.review/diff.txt` and write the report. If user said "against main", use `main` as base.
2. **Staged/local:** Run the script with `--staged` or `--local` instead of branch names when the user asks for that.
3. **User already ran the script:** If `.review/diff.txt` exists and user asks to review it, skip running the script; read the diff and produce the review doc under `.review/`.

Output: write the review to `.review/review-<branch-or-name>.md` (git-ignored). See **Workflow** above for full details.
