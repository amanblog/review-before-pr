# Configuration Guide

The review-before-pr skill can be customized using a `.reviewrc` configuration file in your project root.

## Quick Start

1. Copy the example configuration:

   ```bash
   cp .cursor/skills/review-before-pr/.reviewrc.example .reviewrc
   ```

2. Edit `.reviewrc` to match your project needs

3. The configuration is automatically loaded when you run the diff generation script

---

## Configuration File Format

The `.reviewrc` file uses JSON format:

```json
{
  "version": "1.0",
  "baseBranch": "main",
  "ignorePatterns": [],
  "additionalExcludes": [],
  "secretPatterns": {
    "enabled": true,
    "customPatterns": []
  },
  "review": {
    "categories": ["security", "performance", "maintainability"],
    "commentPriorities": true,
    "contextGathering": true
  },
  "output": {
    "format": "markdown",
    "includeMetrics": true,
    "timestampReports": true
  },
  "patches": {
    "autoGenerate": false,
    "requireConfirmation": true
  }
}
```

---

## Configuration Options

### Basic Settings

#### `version` (string)

- **Default:** `"1.0"`
- **Description:** Configuration file version for future compatibility
- **Example:** `"1.0"`

#### `baseBranch` (string)

- **Default:** `"main"`
- **Description:** Default base branch for comparisons
- **Example:** `"develop"`, `"master"`, `"main"`

---

### Filtering Options

#### `ignorePatterns` (array of strings)

- **Default:** `[]`
- **Description:** Additional file patterns to exclude from diffs (uses glob syntax)
- **Example:**
  ```json
  "ignorePatterns": [
    "*.lock",
    "dist/*",
    "*.min.js",
    "*.generated.ts",
    "migrations/*",
    "test-fixtures/**"
  ]
  ```

**Built-in patterns (always excluded unless `--no-filter` is used):**

- Lock files: `package-lock.json`, `yarn.lock`, `Cargo.lock`, etc.
- Binary files: `*.svg`, `*.png`, `*.jpg`, `*.pdf`, etc.
- Minified files: `*.min.js`, `*.min.css`, `*.bundle.js`
- Build outputs: `dist/`, `build/`, `node_modules/`, `target/`
- Temp files: `*.log`, `*.tmp`, `.DS_Store`

#### `additionalExcludes` (array of strings)

- **Default:** `[]`
- **Description:** Additional git pathspec exclusions (advanced)
- **Example:**
  ```json
  "additionalExcludes": [
    ":!**/test-data/**",
    ":!**/*.snap"
  ]
  ```

---

### Security Options

#### `secretPatterns` (object)

**`secretPatterns.enabled`** (boolean)

- **Default:** `true`
- **Description:** Enable/disable secret detection
- **Example:** `true`

**`secretPatterns.customPatterns`** (array of objects)

- **Default:** `[]`
- **Description:** Add custom secret detection patterns
- **Example:**
  ```json
  "secretPatterns": {
    "enabled": true,
    "customPatterns": [
      {
        "name": "internal_api_key",
        "pattern": "INTERNAL_[A-Z0-9]{32}"
      },
      {
        "name": "custom_token",
        "pattern": "tk_[a-zA-Z0-9]{40}"
      }
    ]
  }
  ```

---

### Review Options

#### `review` (object)

**`review.categories`** (array of strings)

- **Default:** `["security", "performance", "maintainability"]`
- **Description:** Focus areas for code review
- **Options:** `"security"`, `"performance"`, `"maintainability"`, `"accessibility"`, `"testing"`
- **Example:**
  ```json
  "review": {
    "categories": ["security", "accessibility", "testing"]
  }
  ```

**`review.commentPriorities`** (boolean)

- **Default:** `true`
- **Description:** Use explicit priority syntax ([Critical], [High], [Medium], [Nit])
- **Example:** `true`

**`review.contextGathering`** (boolean)

- **Default:** `true`
- **Description:** Enable AI to search codebase for related code during review
- **Example:** `true`

---

### Output Options

#### `output` (object)

**`output.format`** (string)

- **Default:** `"markdown"`
- **Description:** Output format for review reports
- **Options:** `"markdown"` (only option currently)
- **Example:** `"markdown"`

**`output.includeMetrics`** (boolean)

- **Default:** `true`
- **Description:** Track review metrics in `.review/metrics.jsonl`
- **Example:** `true`

**`output.timestampReports`** (boolean)

- **Default:** `true`
- **Description:** Include timestamp in review report filenames
- **Example:** `true`

---

### Patch Options

#### `patches` (object)

**`patches.autoGenerate`** (boolean)

- **Default:** `false`
- **Description:** Automatically generate patch files for suggested fixes
- **Example:** `false` (recommended for safety)

**`patches.requireConfirmation`** (boolean)

- **Default:** `true`
- **Description:** Require user confirmation before applying patches
- **Example:** `true`

---

### PR Comments Options

#### `prComments` (object)

**`prComments.enabled`** (boolean)

- **Default:** `true`
- **Description:** Enable the option to post review findings as pending PR comments
- **Example:** `true`

**`prComments.signature`** (string)

- **Default:** `"🔍 *Posted by review-before-pr — AI-assisted review*"`
- **Description:** Custom signature appended to each PR comment. Set to empty string to disable.
- **Example:** `"🤖 Reviewed by my-team-bot"`

**`prComments.defaultMode`** (string)

- **Default:** `"select"`
- **Description:** Default selection mode when posting comments
- **Options:** `"all"` (post everything), `"select"` (interactive picker), `"skip"` (never offer)
- **Example:** `"select"`

---

### Multi-Pass Review Options

#### `multiPass` (object)

**`multiPass.enabled`** (boolean)

- **Default:** `true`
- **Description:** Enable the verification pass that checks for missed findings after the initial review
- **Example:** `true`

**`multiPass.skipBelowLines`** (integer)

- **Default:** `100`
- **Description:** Skip the verification pass for diffs smaller than this many lines (small diffs rarely benefit from a second pass)
- **Example:** `100`

---

## Example Configurations

### Minimal Configuration

```json
{
  "version": "1.0",
  "baseBranch": "main"
}
```

### Frontend Project (React/Next.js)

```json
{
  "version": "1.0",
  "baseBranch": "main",
  "ignorePatterns": ["*.generated.ts", "*.stories.tsx", "public/static/**"],
  "review": {
    "categories": ["security", "accessibility", "performance"],
    "commentPriorities": true,
    "contextGathering": true
  }
}
```

### Backend Project (Node.js/Python)

```json
{
  "version": "1.0",
  "baseBranch": "develop",
  "ignorePatterns": ["migrations/*", "*.pyc", "__pycache__/**"],
  "secretPatterns": {
    "enabled": true,
    "customPatterns": [
      {
        "name": "internal_api_key",
        "pattern": "INTERNAL_KEY_[A-Z0-9]{32}"
      }
    ]
  },
  "review": {
    "categories": ["security", "performance", "maintainability"],
    "commentPriorities": true,
    "contextGathering": true
  }
}
```

### Monorepo Configuration

```json
{
  "version": "1.0",
  "baseBranch": "main",
  "ignorePatterns": [
    "packages/*/dist/**",
    "packages/*/build/**",
    "*.generated.*",
    "apps/*/public/**"
  ],
  "review": {
    "categories": ["security", "performance", "maintainability", "testing"],
    "commentPriorities": true,
    "contextGathering": true
  },
  "output": {
    "includeMetrics": true,
    "timestampReports": true
  }
}
```

---

## Per-Team Customization

Different teams can use different configurations by placing `.reviewrc` in their respective directories. The script will use the configuration from the nearest parent directory.

Example structure:

```
project-root/
├── .reviewrc                    # Root config (default)
├── frontend/
│   ├── .reviewrc               # Frontend-specific config
│   └── src/
└── backend/
    ├── .reviewrc               # Backend-specific config
    └── src/
```

---

## Validation

The configuration file is validated when loaded. Common errors:

- **Invalid JSON:** Check for missing commas, quotes, or brackets
- **Unknown fields:** Typos in field names will be ignored with a warning
- **Invalid values:** Wrong data types will use defaults

To test your configuration:

```bash
# Run diff generation with verbose output
./scripts/generate_diff.sh --staged

# Check for "Loading configuration from .reviewrc" message
```

---

## Environment Variables

Some settings can be overridden with environment variables:

- `REVIEW_BASE_BRANCH` - Override default base branch
- `REVIEW_ALLOW_SECRETS` - Set to `"true"` to disable secret detection
- `REVIEW_NO_FILTER` - Set to `"true"` to disable file filtering

Example:

```bash
REVIEW_BASE_BRANCH=develop ./scripts/generate_diff.sh --staged
```

---

## Advanced: Custom Review Rules

For team-specific review rules, create a `TEAM_REVIEW_RULES.md` file in your project root. The AI will automatically load and apply these rules during review.

Example `TEAM_REVIEW_RULES.md`:

```markdown
# Team-Specific Review Rules

## Our Conventions

1. Always use our custom error handler: `import { handleError } from '@/lib/errors'`
2. Database queries must use our query builder, not raw SQL
3. All API endpoints must have rate limiting
4. Use Zod for input validation, not manual checks

## Architecture Patterns

- Feature folders: `features/<feature-name>/{components,hooks,api,types}`
- No circular dependencies between features
- Shared code goes in `lib/` or `components/shared/`
```

---

## Troubleshooting

### Configuration not loading

1. Check file location: `.reviewrc` must be in project root
2. Validate JSON syntax: Use `jsonlint` or an online validator
3. Check file permissions: Ensure file is readable

### Patterns not working

1. Test glob patterns with `git ls-files | grep <pattern>`
2. Remember: patterns are relative to project root
3. Use `:!` prefix for git pathspec exclusions

### Need help?

- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Check example configs in `.reviewrc.example`
- Open an issue on GitHub with your configuration
