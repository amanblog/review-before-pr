# Code review checklist (generic)

Use this when running the review-before-pr skill. Apply the sections that match the repo (frontend, backend, or both). These categories are aligned with common industry and community practice (see references below).

---

## General (any stack)

Based on [Google's "What to look for in a code review"](https://google.github.io/eng-practices/review/reviewer/looking-for.html) and common team checklists.

### Design
- [ ] Does the change belong in this codebase and integrate well with the rest of the system?
- [ ] Is the design clear at the level of the CL (files, functions, modules)?
- [ ] Is complexity justified, or is the code more complex than it needs to be?
- [ ] Is the author solving a current problem rather than speculative future ones (no over-engineering)?

### Functionality
- [ ] Does the code do what was intended and is that intent correct for users/developers?
- [ ] Edge cases: null/undefined, empty collections, boundary values.
- [ ] Concurrency: race conditions, deadlocks, or shared mutable state?
- [ ] Error paths and failure modes handled (network, validation, external services)?

### Complexity
- [ ] Can readers understand the code quickly?
- [ ] Are functions/classes/files a reasonable size, or do they need to be broken up?
- [ ] Avoid unnecessary abstraction or "clever" code.

### Tests
- [ ] Are there unit, integration, or e2e tests as appropriate for the change?
- [ ] Do the tests actually fail when the code is broken (no false positives)?
- [ ] Are tests readable and maintainable (no unnecessary complexity)?

### Naming & comments
- [ ] Names clearly communicate what things are or do, without being overly long.
- [ ] Comments explain *why* where necessary; avoid comments that only restate *what* the code does.
- [ ] Stale TODOs or misleading comments removed or updated.

### Style & consistency
- [ ] Matches the project's style guide and existing patterns.
- [ ] No large, unrelated style or formatting changes mixed with functional changes.
- [ ] If the style guide and existing code conflict, prefer the style guide and add a TODO to fix the rest.

### Documentation
- [ ] If behavior, APIs, or setup change, is documentation (README, API docs, runbooks) updated?
- [ ] If code is removed or deprecated, is related documentation removed or updated?

---

## Frontend (React / TS / Vite / similar)

Synthesized from [Graphite](https://graphite.dev/guides/best-practices-reviewing-front-end-code), [DEV Community](https://dev.to/padmajothi_athimoolam_23d/react-code-review-essentials-a-detailed-checklist-for-developers-20n2), [Better Programming](https://betterprogramming.pub/what-you-should-inspect-in-a-front-end-code-review-4010e1bc285a), and [Wayne Thompson's React checklist](https://www.waynethompson.com.au/blog/React-Code-Review-Checklist/).

### Correctness & bugs
- [ ] **Hooks**: Rules of hooks (only at top level; no conditionals/loops); dependency arrays complete and stable.
- [ ] **Async + lifecycle**: No setState (or equivalent) after unmount; use a cancelled flag, AbortController, or cleanup to ignore stale results.
- [ ] **Resource cleanup**: Any created resources (e.g. `URL.createObjectURL`, subscriptions, timers) are released in cleanup or when replaced.
- [ ] **Lists**: Stable, unique keys; avoid index-as-key when the list can reorder or change.
- [ ] **Optional props**: Documented defaults applied in destructuring or component logic so callers get consistent behavior.

### Security
- [ ] No secrets, API keys, or tokens in client code or in the diff.
- [ ] User input is escaped or sanitized; no unsanitized use of `dangerouslySetInnerHTML` (or equivalent).
- [ ] Protected routes and auth checks still apply; no logic that bypasses authentication or authorization.

### Edge cases & error handling
- [ ] Null/undefined guarded (optional chaining, early returns, or explicit checks).
- [ ] Empty and loading states handled; no blank or broken UI when data is missing or slow.
- [ ] Network and API failures handled; no unhandled promise rejections or silent failures in the diff.
- [ ] When inferring types (e.g. from URL or response), wrong or missing server metadata (e.g. Content-Type) is handled.

### Performance
- [ ] Lazy-loaded routes or components have a visible Suspense fallback (e.g. spinner or skeleton), not `null`.
- [ ] Heavy libraries or large modules loaded on demand where appropriate; main bundle not bloated unnecessarily.
- [ ] Unnecessary re-renders or missing memoization only called out when clearly in scope of the change.

### Code quality & consistency
- [ ] Duplication: repeated logic extracted to shared utilities or components where it appears in multiple places.
- [ ] Naming: clear and consistent with the rest of the codebase.
- [ ] Error handling: no empty catch blocks that swallow errors without logging or user feedback.
- [ ] i18n: user-facing strings use translation keys; removed keys are not still referenced elsewhere.

### HTML & semantics
- [ ] Semantic HTML used where appropriate (`header`, `main`, `section`, `article`, `nav`, etc.) instead of only `div`/`span`.
- [ ] ARIA roles and attributes used where needed for screen readers and assistive tech.

### CSS (when CSS changes are in the diff)
- [ ] Styles scoped appropriately; no unintended side effects on other components.
- [ ] Responsive behavior and media queries consistent with the rest of the app.
- [ ] Naming (e.g. BEM or project convention) and specificity (e.g. prefer classes over IDs for styling) consistent.

### Accessibility (when UI changes are in the diff)
- [ ] Interactive elements are focusable and keyboard-navigable; focus not trapped without a way to escape.
- [ ] Form inputs have associated labels or `aria-label`.
- [ ] Link and button text is descriptive (avoid "click here").
- [ ] Images have appropriate `alt` text; color contrast sufficient for text.

### Cross-browser & standards (when relevant)
- [ ] Polyfills or fallbacks for unsupported features if the project supports older browsers.
- [ ] No reliance on non-standard or deprecated APIs without a fallback.

---

## Backend (API / services / data layer)

Common themes from security and backend review checklists (e.g. [Bito](https://bito.ai/blog/code-review-checklist), [Dualite](https://dualite.dev/blog/secure-code-review-checklist)).

### Correctness & bugs
- [ ] **Idempotency**: Mutating operations that should be retry-safe use idempotency keys or upsert-style logic where required.
- [ ] **Transactions**: Multi-step DB or external calls use transactions or compensating logic where consistency is required.
- [ ] **Concurrency**: Race conditions (e.g. double booking, duplicate creation) considered and mitigated.

### Security
- [ ] **Input**: All inputs validated and sanitized; no raw user input in queries or commands (injection-safe).
- [ ] **Authz**: Every protected endpoint or operation checks permissions; no privilege escalation paths.
- [ ] **Logging**: No PII or secrets in logs; error messages do not leak internal details to clients.

### Edge cases & errors
- [ ] Errors mapped to safe HTTP status codes and user-facing messages; no stack traces or internal details exposed.
- [ ] Timeouts and limits on long-running or bulk operations to avoid resource exhaustion.

### Code quality & consistency
- [ ] Single responsibility; avoid god functions or modules.
- [ ] Fail fast: invalid state or input rejected early with clear errors.
- [ ] Consistency with existing service/repository patterns in the repo.

---

## How to use this checklist

- **Prefer actionable feedback**: Report items with **file + location + suggested code in the review doc** where it helps.
- **Don't nitpick**: Skip style points already enforced by linter/formatter unless they affect readability or consistency.
- **Call out positives**: Note good design, clear naming, solid tests, and helpful abstractions ([Google: "Good Things"](https://google.github.io/eng-practices/review/reviewer/looking-for.html#good-things)).
- **Context**: Consider the whole file and system; flag changes that worsen overall code health even if locally they look small.

### Further reading

- [Google eng-practices: What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [Graphite: Best practices for reviewing front-end code](https://graphite.dev/guides/best-practices-reviewing-front-end-code)
- [DEV: React code review essentials](https://dev.to/padmajothi_athimoolam_23d/react-code-review-essentials-a-detailed-checklist-for-developers-20n2)
- [Code review checklist: 40 questions (Augment)](https://www.augmentcode.com/guides/code-review-checklist-40-questions-before-you-approve)
