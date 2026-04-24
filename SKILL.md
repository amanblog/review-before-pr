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

### Step 1.5: Load configuration

Before analyzing, check for a `.reviewrc` at the project root. The diff script already loads general settings (ignore patterns, secret detection). The reviewer should additionally read the optional **`projectConventions`** block and use it as authoritative repo-specific hints:

- `preferredComponents` — e.g. `{ "Button": "CustomButton", "Table": "CustomTable" }`. Flag when the diff builds a custom version of one of these instead of reusing.
- `singletons` — shared service instances the diff should import (e.g. `shared/services/instance`).
- `helpers` — canonical helpers that frequently get reimplemented inline (e.g. `isArabicLocale`, `buildSocialHref`).
- `constants` — shared constants / enums the diff should use instead of raw values (e.g. `STORE_DOMAIN`, `CourseSortBy`).
- `locales` — configured locale codes. Hardcoded user-visible strings need translations in **all** of these.
- `isNextJs` — if `false`, flag `'use client'` directives as no-ops.
- `importStyle` / `pathAlias` — `"absolute"` + `"@/"` means relative `../../` imports in the diff should be flagged.

See `.reviewrc.example` for the full shape. If `projectConventions` is absent, apply the same checks generically using repo inspection (grep for `custom-*.tsx`, check `shared/services/`, etc).

### Step 2: Scan-first, then deep-dive

Load the checklist at **`references/REVIEW_CHECKLIST.md`** — it opens with a **Scan-First Trigger Matrix** organized by area (styling/tokens, component reuse, types, i18n, React, data fetching, routing, auth flows, forms, performance, mobile, empty states, security, dead code, monorepo, repetition).

**Pass 1 — trigger scan (cheap, covers ~80% of findings):** scan the diff once against the trigger matrix. For each trigger that matches, run the prescribed check and file a finding. The trigger list is ordered to front-load the patterns that appear in real PR reviews — don't skip rows because they look obvious; the obvious ones are what reviewers most often miss.

**Pass 2 — deep read:** read the diff file by file and flag anything the trigger pass didn't catch. Stay disciplined: skip "naming could be clearer" or "add a comment here" unless it materially blocks understanding. The checklist's "General principles" section is for your mental posture, not for filing generic findings.

**Large diffs (5,000+ lines):** summarize findings by file or module rather than line-by-line. Prioritize Critical and High; group Mediums by theme. Note in the review doc that a full line-by-line review wasn't feasible.

### Step 2.5: Context gathering (trigger-driven)

The trigger matrix tells you *when* to search; this step tells you *how*. For every trigger that matches, search the repo before filing the finding — if the "missing" thing already exists elsewhere, don't flag it; if it's truly absent, the finding is sharper with the concrete reference.

- **Changed export signatures** — grep every call site. Do they pass the new param / handle the new field?
- **New component / hook / util** — search for `preferredComponents` names from `.reviewrc`; search for files matching `custom-*.tsx`, `shared/components/*`, `packages/*` in a monorepo.
- **New service instance** — grep for `shared/services/instance` (or whatever the `.reviewrc.singletons` entry names).
- **Tailwind arbitrary values** — grep the repo's theme / tokens file for the actual value, so you can suggest the correct token name.
- **New user-visible string** — grep the `en/*.json` locale file for the string; if absent, flag translation gap (and in **all** `locales` from `.reviewrc`).
- **Real API replacing mocks** — grep the same module for `mock-*`, `MOCK_*`, `DUMMY_*` that should be deleted.
- **i18n JSON edited** — scan the same file for duplicate keys (later wins silently).
- **Filters / pickers added** — check sibling data components in the same page: do they all respect the new filter?
- **Monorepo change** — before adding to `apps/X/`, check `packages/*` and other `apps/*` for an existing implementation.

This prevents false-positive findings where the "missing" thing actually exists and the diff should just use it.

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

**Rules for the `**File:**` reference:**

- Always include a line number: `` **File:** `path/to/file.ext:42` ``.
- For multi-line issues, use a range — the comment will anchor to the first line: `` `path/to/file.ext:42-58` ``.
- If the finding spans multiple files, write each on its own finding or pick the primary file — the parser reads the first `` `path:line` `` reference.
- If the finding is genuinely file-wide (no specific line), still write the file path. The posting script will anchor the PR comment to the first added line in that file from the diff, so you do not need to invent a line — but prefer a concrete line whenever one fits.

### Step 3.5: Verification Pass (Multi-pass Review)

**IMPORTANT: The first pass (Step 3) must be thorough and complete on its own.** Do not hold back findings or reduce depth because a second pass exists. The verification pass is a _safety net_, not a substitute for a comprehensive first pass. Report every issue you find in Step 3 — err on the side of more findings, not fewer.

After producing the initial review document, do a **focused second pass** to catch findings that the first pass may have missed. This is not a full re-review — it is a targeted gap check using specific lenses that complement the first pass.

**How to run the verification pass:**

1. Re-read **all findings** in your review document to know what is already covered.
2. Re-scan the diff with these specific lenses, checking **only** for things not already covered:
   - **Cross-file issues**: Are there patterns or inconsistencies _across_ files that individual-file review missed? (e.g., an API contract changed in one file but callers in another file weren't updated)
   - **Security blind spots**: Any input validation, auth checks, or injection vectors missed?
   - **Error paths**: Are there unhappy paths (network failures, null/empty inputs, timeouts) not handled?
   - **Concurrency & state**: Race conditions, shared mutable state, missing locks?
   - **Missing tests**: Are there new code paths with no corresponding test coverage?
3. If the second pass finds new issues, **append them to the existing review document** under their appropriate priority section (do not rewrite findings from pass 1). Add a note like:

   ```markdown
   > _Found in verification pass_
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
{
  "timestamp": "2026-03-16T10:30:00Z",
  "branch": "feature-auth",
  "mode": "branch",
  "base": "main",
  "diff_lines": 342,
  "files_changed": 12,
  "findings": { "critical": 2, "high": 5, "medium": 8, "positive": 3 },
  "secrets_detected": 0,
  "duration_seconds": 45
}
```

This allows users to track review patterns over time and measure code quality improvements.

### Step 5: Post Comments to PR

**IMPORTANT: Always run this step after producing the review document.** Do not skip this step unless the review mode is `--staged` or `--local` (no PR exists for local-only changes).

After the review document is generated, check if the current branch has an open PR. If a PR is detected, you **must** ask the user whether they want to post the findings as pending review comments on the PR.

**How this works:**

1. **Detect PR:** Run `gh pr view --json number,url` to check for an open PR on the current branch. If `gh` is not installed or no PR exists, inform the user ("No open PR found for this branch — skipping PR comment posting. You can still use the review doc at `.review/review-<branch>.md`.") and stop here.

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
🔍 *Posted by review-before-pr — AI-assisted review*
```

**Requirements:**

- `gh` CLI must be installed and authenticated (`gh auth status`)
- Current repo must have a GitHub remote
- A PR must exist for the current branch (or `--pr` flag used)

**When to skip:** Only skip this step if (a) the review mode is `--staged` or `--local` (no PR context), or (b) `gh` CLI is not installed/authenticated. For all branch-vs-branch reviews, always check for a PR and ask the user.

## Output template

Use this structure in the generated review doc (follow the priority syntax from the checklist):

````markdown
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
````

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
4. **After writing the review (branch-vs-branch mode only):** Run `gh pr view --json number,url` to check for an open PR. If found, ask the user: *"PR #N detected. Would you like to post review comments to this PR? (all / select / skip)"*. Then run `python3 "<skill-dir>/scripts/post_comments.py" .review/review-<branch>.md` with the appropriate flags. **Do not skip this step** — always check for a PR and ask.

Output: write the review to `.review/review-<branch-or-name>.md` (git-ignored). See **Workflow** above for full details.
```
