# Code Review Checklist v2.1 — Elite Edition

*Based on Google, Microsoft, Meta, Netflix, and Stripe engineering standards*

---

## Meta-Instruction for AI Reviewers

**Core Philosophy (Google Standard):**

> Approve changes that **improve overall code health**, even if not perfect.  
> Favor continuous improvement over perfection.

**Review Layers (Meta Engineering):**

1. **Design & architecture** FIRST
2. **Security & correctness** SECOND  
3. **Performance & maintainability** THIRD
4. **Style & nits** LAST (only if blocking)

**Comment Priority Syntax (Esri + Industry):**

- `[Critical]` - Blocks merge (security, data loss, broken functionality)
- `[High]` - Should fix (logic errors, important edge cases)
- `[Medium]` - Good to address (refactors, consistency)
- `[Nit]` - Optional style preference
- `[Positive]` - Well done! (always include these)

---

## Few-Shot Examples (Gemini Method)

### ❌ BAD Review Comment

> "Consider using a ternary operator here instead of an if/else block."

**Why bad:** Subjective style nitpick with no impact on code health.

### ✅ GOOD Review Comment

> **[Critical]** `auth.ts:45` - The `getUser` function does not handle the case where the database connection drops, causing an unhandled promise rejection. This will crash the server in production.
> 
> **Suggested fix:**
> ```typescript
> try {
>   const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
>   return user;
> } catch (error) {
>   logger.error('DB connection failed', { userId, error });
>   throw new ServiceUnavailableError('Database temporarily unavailable');
> }
> ```
> 
> **Why this matters:** Database connection failures are common in production (network issues, maintenance windows). Without proper error handling, this will cause server crashes and poor user experience.

**Why good:** Specific location, clear impact, actionable fix with code, explains business impact.

---

## General (All Stacks)

### 1. Code Health Mindset (Google + Microsoft)

- [ ] Does this change **improve** overall code health?
- [ ] Would future developers be happy this exists?
- [ ] Is complexity justified for **current** needs (not speculative future)?

### 2. Design & Architecture (Google #1 Priority)

- [ ] **Every Line Rule**: Have you looked at every line of human-written code?
- [ ] Does it belong here or in a shared module/library?
- [ ] Integrates cleanly with existing system?
- [ ] No over-engineering for problems that don't exist yet?
- [ ] Single responsibility principle followed?
- [ ] **Reuse check** *(trigger: new hook, service, util, or type is created)*: Search for existing implementations of similar functionality elsewhere in the codebase. Flag when the diff creates a new hook/service/util that duplicates what already exists in another module.
- [ ] **Singleton & shared-instance check** *(trigger: diff instantiates service classes like `new AxiosRestService()`, `new HttpAuthService()`, etc.)*: Verify the project has a shared instance (e.g. `shared/services/instance.ts`). Flag when the diff creates its own instance instead of importing the singleton — duplicate auth/interceptor state causes subtle bugs.

### 3. Functionality & Correctness (Meta Tracing Method)

- [ ] **Trace critical paths line-by-line** (auth, payments, data mutations)
- [ ] Edge cases: null/undefined, empty collections, boundary values
- [ ] Concurrency: race conditions, deadlocks, shared mutable state
- [ ] Error paths: network failures, validation errors, external service failures
- [ ] Off-by-one errors, wrong loop conditions
- [ ] **Validation thoroughness** *(trigger: diff contains regex patterns, string equality checks on API values, or timeout/event handlers)*: Test regex against adversarial inputs (e.g., does a phone regex accept `-----`?). Check that numeric comparisons don't rely on exact string matching (e.g., `price === '0.000'` vs `Number(price) === 0`). Verify event handlers have their triggers actually wired (e.g., `xhr.ontimeout` set but `xhr.timeout` never assigned).
- [ ] **Monetary/financial data** *(trigger: diff uses `parseFloat`/`Number()` on price, amount, or currency strings)*: Flag raw float arithmetic on monetary values — recommend display-only parse helpers. If the backend sends decimals as strings, ensure they stay as strings until display formatting.

### 4. Security (OWASP + Industry)

- [ ] **Input validation**: All user inputs sanitized at entry points?
- [ ] **Authentication/Authorization**: Checks present? No privilege escalation?
- [ ] **Secrets**: No hardcoded API keys, passwords, tokens?
- [ ] **Injection**: SQL/NoSQL/Command injection prevented (parameterized queries)?
- [ ] **Logging**: No PII or secrets in logs? Safe error messages?

### 5. Tests (Google + Microsoft)

- [ ] Appropriate tests added in same change (unit/integration/e2e)?
- [ ] Tests actually fail when code breaks (no false positives)?
- [ ] Edge cases and failure modes tested?
- [ ] Tests readable and maintainable?

### 6. Performance (Senior Engineer Standards)

- [ ] No N+1 queries or obvious performance regressions?
- [ ] Expensive operations inside loops?
- [ ] Missing indexes on database queries?
- [ ] Caching opportunities where appropriate?
- [ ] Memory leaks possible (unclosed resources)?

### 7. Readability & Maintainability

- [ ] Can another developer understand this quickly?
- [ ] Functions/classes reasonable size (not god objects)?
- [ ] Naming clear and communicative?
- [ ] Comments explain *why*, not *what*?
- [ ] No unnecessary abstraction or "clever" code?

### 8. Style & Consistency

- [ ] Matches project style guide and existing patterns?
- [ ] No unrelated formatting changes mixed in?
- [ ] Linter/formatter rules followed?
- [ ] **Existing constants/variables check** *(trigger: diff contains hardcoded color values, magic strings, domain URLs, or repeated literals)*: Search for existing constants files (`constants.ts`, `config.ts`, design tokens) in the project. Flag when a value already exists as a shared constant, CSS variable, or Tailwind token.
- [ ] **Dead code & mock cleanup** *(trigger: diff adds real API integration, new service, or replaces mock data)*: Check if old mock files, mock constants, placeholder types, or commented-out code in the same module are now obsolete. Flag leftover mocks and unexplained commented-out code.

### 9. Documentation

- [ ] APIs, behavior changes documented?
- [ ] README/setup docs updated if needed?
- [ ] Stale docs removed?

---

## Frontend-Specific (React/TS/Next.js)

### React Hooks & Lifecycle

- [ ] Rules of hooks followed (top-level only, no conditionals)?
- [ ] Dependency arrays complete and stable?
- [ ] No setState after unmount (cleanup with AbortController)?
- [ ] Resource cleanup (timers, subscriptions, object URLs)?
- [ ] **Ineffective memoization** *(trigger: diff contains `useCallback`/`useMemo` with dependency arrays)*: Check if any dependency is an unstable reference that recreates every render (e.g., mutation objects from `useMutation()`, inline objects). If so, the memoization is a no-op — flag it for removal or stabilization via refs.

### Lists & Keys

- [ ] Stable, unique keys (not index-as-key on dynamic lists)?

### Error & Loading States

- [ ] Empty/loading/error states handled?
- [ ] Suspense fallbacks visible (not null)?
- [ ] No unhandled promise rejections?
- [ ] **UX consistency** *(trigger: diff adds filters, state toggles, or data-scoped UI sections)*: Do filters/state changes affect **all** related UI sections consistently? (e.g., a month picker that filters earnings but not the sales table below it). Check that loading states disable sibling interactive elements (e.g., disable Delete while Edit is loading). Verify displayed data includes sufficient context — dates show month/year, amounts show currency.

### Accessibility (WCAG 2.1 AA)

- [ ] Semantic HTML (`header`, `main`, `nav` not just `div`)?
- [ ] ARIA roles/labels where needed?
- [ ] Keyboard navigation works?
- [ ] Form inputs have labels?
- [ ] Color contrast sufficient?

### Performance

- [ ] Lazy loading with proper fallbacks?
- [ ] No unnecessary re-renders?
- [ ] Bundle size impact considered?

### Security

- [ ] No `dangerouslySetInnerHTML` without sanitization?
- [ ] Protected routes have auth checks?
- [ ] No secrets in client code?

### i18n & RTL *(trigger: project uses i18n/translation library, or serves RTL locales like Arabic/Hebrew)*

- [ ] **Duplicate translation keys**: When diff modifies JSON translation files, check for duplicate keys in the same file — later duplicates silently override earlier ones.
- [ ] **RTL-aware icons & layout**: Directional icons (chevrons, arrows, sliders) must flip for RTL. Check for `ChevronRight` without a corresponding `ChevronLeft` for RTL, or hardcoded `left`/`right` CSS without logical equivalents (`start`/`end`).
- [ ] **Hardcoded locales**: Flag hardcoded `'en-US'` or similar in `Intl.DateTimeFormat`, `toLocaleDateString`, `toLocaleString`, etc. when the app supports multiple locales. Use the app's locale context instead.
- [ ] **Fragile translation keys from API values**: Flag when raw API response strings (e.g., `"Bank Transfer"`, `"COMPLETED"`) are used directly as i18n keys — these break when the backend changes casing or wording. Map API enums to stable translation keys explicitly.

### Type Safety *(trigger: diff contains `: any`, untyped API responses, or loose type assertions)*

- [ ] **No `any` in API layers**: Flag `any` on mutation payloads, service method params/returns, hook return types, and API response types. When a typed interface exists, use it. When it doesn't, create one from the API contract/docs.
- [ ] **Component prop usage** *(trigger: diff applies className/style overrides to a component)*: Check if the component already exposes a prop for that behavior (e.g., `variant`, `size`, `disabled`). Flag redundant classNames that duplicate existing component API.

---

## Backend-Specific (API/Services/Data)

### Correctness

- [ ] **Idempotency**: Retry-safe operations use idempotency keys?
- [ ] **Transactions**: Multi-step operations use transactions?
- [ ] **Concurrency**: Race conditions mitigated (locks, optimistic locking)?

### Security

- [ ] **Input validation**: All inputs validated/sanitized at entry?
- [ ] **Authorization**: Every protected endpoint checks permissions?
- [ ] **SQL Injection**: Parameterized queries used?
- [ ] **Error responses**: No stack traces or internal details exposed?

### Error Handling

- [ ] Timeouts on external calls?
- [ ] Rate limiting where appropriate?
- [ ] Graceful degradation on failures?

### Logging & Observability

- [ ] Useful logs at appropriate levels?
- [ ] No PII in logs?
- [ ] Correlation IDs for request tracing?

---

## Positive Notes (Google "Good Things")

**Always call out:**

- Elegant design solutions
- Excellent test coverage
- Clear naming conventions
- Helpful abstractions
- Performance optimizations
- Security best practices
- Knowledge-sharing comments

---

## Change Size Guidance (Meta/Google)

**Ideal:** ≤ 400 lines of meaningful change  
**Maximum:** 1000 lines (beyond this, review effectiveness drops 75%)

**If diff is too large:**

> **[Medium]** This change is quite large (X lines). Consider breaking into smaller, logical PRs:
> 
> 1. Core functionality
> 2. Tests
> 3. Documentation
> 
> Smaller changes are easier to review thoroughly and safer to merge.

---

## Context Gathering Instructions (Gemini Method)

**For AI Reviewers:**

When reviewing a diff, you lack full context. You MUST proactively search:

1. **Modified exports**: If a function/type signature changes, search where it's imported
2. **New dependencies**: If unfamiliar modules imported, read those files first  
3. **Database schemas**: If Prisma/TypeORM models change, check migrations
4. **API contracts**: If endpoints change, verify client code compatibility

**Example:**

```
Diff shows: export function getUser(id: string, includeDeleted: boolean)
Action: Search codebase for "getUser(" to find all call sites
Check: Do they pass the new boolean parameter?
```

### Trigger-Based Context Searches

These searches are **conditional** — only run them when the trigger pattern appears in the diff. This keeps token usage low while catching issues that pure diff review misses.

| Trigger in diff | Search action | What to flag |
|---|---|---|
| Hardcoded color values, magic strings, domain URLs | Search for `constants.ts`, `config.ts`, design token files in the project | Value already exists as a shared constant or token |
| `new AxiosRestService()`, `new Http*Service()`, or similar class instantiation | Search for `shared/services/instance` or equivalent singleton file | Diff creates its own instance instead of importing the shared one |
| New hook, service class, or utility function | Search for existing implementations with similar names/purposes | Duplicate functionality already exists in another module |
| Real API integration replacing mock/placeholder | Search same module for leftover mock files, mock constants, placeholder types | Dead code that should be cleaned up in the same PR |
| `useCallback`/`useMemo` with dependency arrays | Check if deps include unstable refs (mutation objects, inline objects) | Memoization is ineffective — deps change every render |
| Regex patterns for validation | Test pattern mentally against adversarial inputs (empty strings, all-dashes, all-spaces) | Regex accepts meaningless or dangerous input |
| `parseFloat`/`Number()` on price/amount/currency | Check if result is used for arithmetic vs display only | Float arithmetic on monetary values — rounding risk |
| Filters, pickers, or state toggles in UI | Check all sibling components that display related data | Filter applies to one section but not another — UX inconsistency |
| Translation/i18n JSON files modified | Scan modified file for duplicate keys | Later duplicate key silently overrides earlier one |
| Raw API string used as translation key | Check if backend could return different casing/format | Fragile key that breaks on backend change |

---

## Output Format Requirements

### For Each Finding:

**[Priority] Category: Brief description**

**File:** `path/to/file.ext:line_number`

**Issue:** Clear explanation of the problem and its impact.

**Suggested fix:**

```language
// Exact code to replace or add
// Must be copy-paste ready
```

**Why this matters:** Brief context on business/technical impact.

---

## Further Reading

- [Google: What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [Google: Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [Microsoft Research: Code Review Best Practices (Michaela Greiler)](https://www.michaelagreiler.com/code-reviews-at-microsoft-how-to-code-review-at-a-large-software-company/)
- [Meta Engineering: Fast Reviews](https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving-developer-experience/)
