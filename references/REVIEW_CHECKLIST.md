# Code Review Checklist v3 — Trigger-First Edition

*Tuned from real PR review patterns (Google, Meta, Stripe standards + field-tested frontend triggers).*

---

## How to use this checklist (for AI reviewers)

1. **Priority syntax** — tag every finding as `[Critical]` (blocks merge), `[High]` (should fix), `[Medium]` (good to address), `[Nit]` (optional), or `[Positive]` (always include some).
2. **Review layers in order**: (a) Design & correctness → (b) Security → (c) Performance & maintainability → (d) Style.
3. **Scan-first pass**: before reading the diff line by line, scan it once against the **Trigger Matrix** below. Each trigger row says *"if the diff contains X, check Y and flag Z."* This is the single most important surface in this document.
4. **Then deep-dive** using the Frontend / Backend / General sections — but only flag what adds signal beyond the triggers. Do **not** file generic findings like "naming could be clearer" or "add a comment here" unless they block understanding.
5. **Project conventions**: read `.reviewrc` in the project root. If it has a `projectConventions` block, treat those names (shared components, constants, helpers, singletons) as authoritative — flag when the diff reinvents what's already listed there.

---

## Scan-First Trigger Matrix

Organized by area. If the trigger pattern appears in the diff, run the check and flag what matches. Cells are written in "trigger → action → what to flag" form so you can scan quickly.

### Styling & design tokens

| Trigger in diff | Check | What to flag |
|---|---|---|
| Arbitrary Tailwind values: `text-[14px]`, `rounded-[16.5px]`, `p-[12px]`, `w-[600px]` | Is there a built-in utility or design-token equivalent? (`text-sm`, `rounded-2xl`, `p-3`, `w-[720px]` from Figma) | Replace arbitrary value with the built-in utility or documented token — keeps type/size scale consistent |
| Arbitrary CSS var as Tailwind class: `text-[var(--color-foo)]`, `bg-[var(--color-primary)]` | Is there a direct token (`text-foreground`) or Tailwind v4 shorthand (`text-(--color-foo)`)? | Replace with semantic token (`text-foreground`, `bg-primary`) or the v4 `(--var)` syntax |
| Hardcoded hex/rgb colors: `#0F172A`, `bg-gray-800`, `border-amber-400` | Is there a semantic token (`bg-foreground`, `border-warning`)? Check project's token/theme file | Use the semantic token so dark-mode / theming stays consistent |
| `className` overrides on a shared component (`<CustomButton className="bg-[...] text-white hover:bg-[...]">`) | Does the component already set those styles by default or via a `variant` prop? | Remove redundant classes; use the component's own API (`variant`, `size`) |
| Hardcoded font-size / radius / spacing that doesn't match the Figma/design | Compare against Figma when the user provides it; otherwise flag numbers that look like pixel-peeped guesses (`16.5px`, `13px`) | Suggest the nearest token or call out the design mismatch |

### Component reuse & design system

| Trigger in diff | Check | What to flag |
|---|---|---|
| New component that looks like a button, table, dialog, modal, chip, input, card, dropdown, tab | Search the project for a shared equivalent (e.g. `shared/components/custom-*`, `components/ui/*`). Check `.reviewrc.projectConventions.preferredComponents` | The project already has `CustomButton` / `CustomTable` / shadcn `Dialog` etc. — reuse instead of reimplementing |
| New service class instantiated: `new AxiosRestService()`, `new HttpAuthService()`, `new AuthorisedRestService()` | Is there a shared singleton (`shared/services/instance.ts`)? Check `.reviewrc.projectConventions.singletons` | Import the singleton — local instances cause duplicate interceptor/auth state |
| New hook, util, or helper with a generic name (`useXYZ`, `formatFoo`, `parseBar`) | Search for existing implementations with similar names/purposes across the monorepo, including `packages/*` | Duplicate logic already exists; extend it or import it |
| Inline helper inside JSX that clearly belongs elsewhere: date formatting, currency formatting, URL building, locale detection | Check `.reviewrc.projectConventions.helpers` (e.g. `isArabicLocale`, `buildSocialHref`, `formatCurrency`) | Use the repo's canonical helper — inline duplicates drift |
| Import path uses a relative `../../` traversal | Does the project's tsconfig have path aliases (`@/`, `~/`)? Do sibling files use the alias? | Use the alias form — keeps imports consistent and refactor-safe |
| `'use client'` directive in a non-Next.js repo (check for `next` in package.json) | Is this actually a Next.js project? | Remove the directive — no effect outside Next.js App Router |

### Types

| Trigger in diff | Check | What to flag |
|---|---|---|
| `: any`, `as any`, `Record<string, any>` | Is the real type available from an API doc, existing interface, or type inference? | Replace with the concrete type. `as any` on already-narrowed unions is almost always wrong |
| Raw string for a field that has only a few valid values (e.g. `currency: string`, `sortBy: string`) | Is there a union type or enum already (`Currency`, `CourseSortBy`)? | Use the narrower type; flag drift when a `type X` enumerates values a sibling constant (`X_OPTIONS`) also enumerates |
| `Partial<Omit<T, 'k'>>` as the payload type | Compare to what the code actually sends — does it include the "omitted" key? | Type lies — either restore the key in the type or drop it from the payload |
| Translation/i18n keys built from raw API strings: `t(response.status)`, `t(\`mode_${response.payment_mode}\`)` | Does the backend guarantee exact casing/format? | Map API enums to stable keys explicitly; raw strings break on backend change |

### i18n & RTL

| Trigger in diff | Check | What to flag |
|---|---|---|
| New user-visible English string in JSX, toast, alert, error message, placeholder, or empty-state | Is it wrapped in `t(...)` (or the project's translation fn)? Does the matching key exist in both `en/` and `ar/` (or all configured locale files)? | Add translation keys in **all** locale files — Arabic parity is routinely forgotten |
| Translation JSON file modified | Scan for duplicate keys in the same file | Later duplicate silently overrides earlier one |
| Existing translation key removed from a locale file | Search the codebase for uses of that key | Dead key or — worse — dangling reference in a component |
| `isRtl` computed inline (`locale === 'ar'`, `document.dir === 'rtl'`) | Does the project have a helper (`isArabicLocale(locale)`, `useIsRtl()`)? Check `.reviewrc.projectConventions.helpers` | Use the shared helper; inline checks drift |
| Directional icons (`ChevronRight`, `ArrowRight`, `<CaretRight>`) or hardcoded `left`/`right` CSS | Is there RTL handling (flip at `dir="rtl"`, logical `start`/`end`)? | Add the RTL flip — chevrons point the wrong way for Arabic users |
| Em dash `—`, en dash `–`, curly quotes `" "` in Arabic translation file | Confirm these render correctly in the target locale | Em dash can break RTL flow; stick to simple hyphens / locale-appropriate punctuation |
| `Intl.*`, `toLocaleDateString`, `toLocaleString` with hardcoded `'en-US'` | Is the app multi-locale? | Pass the current locale from the app's i18n context |
| Empty `alt=""` on `<img>` that's not purely decorative | Is the image informational? | Add meaningful `alt` — wrap in `t()` like any other visible string |

### React patterns

| Trigger in diff | Check | What to flag |
|---|---|---|
| `useCallback` / `useMemo` with a deps array | Are any deps unstable references (inline objects, mutation objects from `useMutation()`, `t` when not memoized)? Is a dep missing entirely? | Ineffective memoization (deps change every render) or lint-suppressible stale-closure risk |
| `useCallback` wrapping a `useState` setter or a plain prop | Is the wrapping doing any work? | React state setters are already stable — the `useCallback` is noise |
| `setState(prev => ...)` where the updater reads a variable from the outer scope | Is that outer value captured or recomputed inside? | Stale state bug — use the `prev` param or move the compute inside |
| `URL.createObjectURL(...)` in the component body | Is it inside a `useMemo` or `useEffect` with a cleanup `URL.revokeObjectURL`? | Memory leak — runs every render; revoke URLs on cleanup |
| Index used as `key` in `.map(...)` on a dynamic list | Is the list ever reordered, filtered, or items inserted? | Use a stable ID — index keys break reconciliation and accessibility focus |
| `useEffect` that auto-focuses or resets scroll/focus without a guarded condition | Does it run on every render or only when it should? | Focus reset on every render breaks keyboard navigation |
| New `useState` that mirrors a prop or derived value | Is it actually needed, or can it be derived? | Unnecessary state; sync bugs waiting to happen |

### Data fetching (React Query / SWR / fetch)

| Trigger in diff | Check | What to flag |
|---|---|---|
| `useQuery({ queryKey: [...], queryFn: ... })` where `queryFn` reads state/filter variables | Are all such variables included in `queryKey`? | Static key → no refetch when the filter/month/currency changes |
| `placeholderData` or `keepPreviousData` on a query keyed by a changing state | Could the placeholder display stale values (e.g. `sales_count` from last month)? | Call this out — users see wrong values during transitions |
| Query with no `enabled` gate on a dependency that can be null (e.g. `userId`, `orgId`) | Is the query guarded with `enabled: !!userId`? | Avoid 401/400 on initial render |
| New mutation without `onError` handling | Does the UI show the failure? | Silent failure; at minimum surface an error toast |
| Response type declared as `any` or `unknown` | Is there an API contract (OpenAPI/yaak/proto doc) | Use the concrete response type |

### Routing & code-splitting

| Trigger in diff | Check | What to flag |
|---|---|---|
| New `<Route>` added to the app router | Do sibling routes use `lazy()` / `React.lazy`? Does this one? | Add `lazy()` to keep the main bundle stable |
| New `<Route>` for authenticated content | Is it wrapped in the project's `ProtectedRoute` / auth guard? | Unprotected route leaks into unauthenticated state |
| Redirect/`navigate()` target path | Does that route exist and match the user's post-auth landing page? (e.g. `/` vs `/home`) | Wrong redirect breaks onboarding |
| Multi-step flow (wizard, onboarding) changes URL | Does the code use shallow routing (Next) or `replace()` so the back button behaves correctly? | Missing shallow routing → browser history blows up |

### Auth flows

| Trigger in diff | Check | What to flag |
|---|---|---|
| OTP / verification screen calls `confirmLogin` / `signIn` / `verify*` | Is the same screen reused for both signup and login? If so, should signup call `confirmSignUp` instead? | Wrong confirmation endpoint; user "verifies" but session never completes |
| Route depends on a possibly-null user (`user!.id`, `session!.token`) | Is there a null guard earlier in the component? | Non-null assertion on async state — crashes before hydration |
| `creator_id` / `owner_id` / similar set from logged-in user on an edit flow | Is this a create or edit? On edit, does it overwrite the actual owner with the logged-in user? | Authorization-level bug: assigning ownership on update |

### Forms & validation

| Trigger in diff | Check | What to flag |
|---|---|---|
| Field loaded into form state (`setValue('show_on_storefront', data.show_on_storefront)`) | Is the same field included in the save payload? | Round-trip break — edit looks like it works but value is never sent |
| Regex for phone / email / URL / username validation | Test against adversarial inputs: empty, all-dashes, all-spaces, emoji, Unicode, leading dots, RTL marks | Regex that accepts `-----` or ` ( ) - ` is not validating anything |
| `<input type="file" accept=".pdf">` | Is there a client-side MIME/extension check after selection? A user-facing error when the wrong file is picked? | `accept` is a UI hint — users can bypass via "All Files" |
| `<input type="number">` on a price / quantity / count | Does the handler reject negatives, scientific notation (`1e9`), `NaN`, `Infinity`? | Accepts `-50` or `1e9` silently |
| Form submit button with an async handler | Is there an in-flight guard (disabled, `isSubmitting`)? Does the same form also auto-submit on completion (OTP autofill)? | Double-submit — auto-submit + button click both fire |
| Error message cleared only on submit | When the user fixes the field, does the error clear? | Stale error stays visible after the user corrected the input |

### Performance

| Trigger in diff | Check | What to flag |
|---|---|---|
| Expression/function call used multiple times in the same render (`user.name.split(' ')[0]` called twice) | Is it cheap? If not, memoize or compute once above the JSX | Repeated expensive call per render |
| `new Date()`, `Date.now()`, `Math.random()` inside render | Is it deterministic between renders? | Non-stable values cause unnecessary re-renders / test flakiness |
| Large inline object/array passed as a memoized hook dep | Same shape, new reference every render | Defeats the memoization |
| List rendering 100+ items without virtualization | Is virtualization needed? | Scroll jank on low-end devices |
| Image `<img src="...">` without `width`/`height` or `loading="lazy"` | Is it above the fold? | CLS and bandwidth issues |

### Mobile & responsive

| Trigger in diff | Check | What to flag |
|---|---|---|
| Changes to header / navbar / sidebar / dialog / drawer / table | Open the file in your head at `sm` (<640px): does it still work? | Mobile regressions — off-center titles, 3-col grids that collide, dialogs that overflow viewport edges |
| Responsive class churn: `sm:text-base text-sm`, `md:p-4 p-2` for tiny differences | Is the breakpoint-specific class actually needed? | Strip noise; one token often covers both |
| Dialog / modal component applied to a page | On mobile, does it go edge-to-edge vs sit in the middle with a gap? Compare with other dialogs in the repo | Design inconsistency on small screens |
| FAB (floating action button) / primary CTA removed from a page | Is there still a mobile entry point for the action? | Users lose the ability to perform the action on mobile |

### Empty / loading / error states

| Trigger in diff | Check | What to flag |
|---|---|---|
| New page or section that fetches data | Is there a loading skeleton, empty state, and error state? Are they separate (not just "loading...")? | Missing states feel broken to users |
| Fallback copy like "N/A", "—", or "0" for missing fields (name, duration, price) | Does the fallback convey **wrong** information? (e.g. "Duration: 0 min" when duration is simply absent) | Hide the field instead of showing a misleading zero |
| Default placeholder avatar/image | When the real data is missing (no name set), does the UI offer a clear action? ("Add your name", clickable) | Empty state should nudge toward the fix, not just blank out |

### Security & secrets

| Trigger in diff | Check | What to flag |
|---|---|---|
| `window.open(url)` or `<a target="_blank">` without `rel="noopener noreferrer"` | Opener access risk | Add `rel="noopener noreferrer"` |
| `dangerouslySetInnerHTML={{ __html: x }}` | Is `x` sanitized? | Add DOMPurify or similar; never trust server HTML blindly |
| User input interpolated into a URL (`buildUrl(\`/\${userInput}\`)`) | Is it encoded (`encodeURIComponent`) and validated? | XSS / open-redirect vectors |
| New env var, API key, or token in the diff | Is it actually committed, not just referenced? Check `.env*` and client bundles | Reject; rotate if already pushed |
| Auth token stored in `localStorage` | Does the threat model allow XSS? | Prefer httpOnly cookies for session tokens |

### Dead code, mocks & repo hygiene

| Trigger in diff | Check | What to flag |
|---|---|---|
| Real API integration replaces mock | Are `mock-*` files, mock constants, placeholder types, or commented-out `// TODO: remove when API is ready` still around? | Remove in the same PR; reviewers won't come back |
| Mock data left in (`mockUsers`, `DUMMY_TRANSACTIONS`, hardcoded lists) | Is the name clearly prefixed (`MOCK_`, `DUMMY_`) so it's obvious at the import site? | Rename with explicit prefix or delete |
| Commented-out code ≥3 lines | Is there a reason note? | Delete; git history is the archive |
| Unused imports, unused state, unused props | If the variable is new or touched, but never read | Delete — `_var` rename is not a fix, it's noise |
| Per-developer config staged: `.claude/settings.local.json`, `.vscode/settings.json`, `.idea/*`, local `.env.local` | Is it in `.gitignore`? | Unstage and add to `.gitignore` — these diverge per developer |

### Monorepo awareness

| Trigger in diff | Check | What to flag |
|---|---|---|
| New component/util/hook in `apps/<app-name>/src/...` | Does `packages/*` already export something equivalent? Does another app under `apps/*` already implement it? | Hoist to the shared package instead of duplicating |
| Shared package (`packages/ui`, `packages/bio-components`) imports from an app | Directionally wrong — packages shouldn't depend on apps | Invert the import or move the symbol |
| Shared component suddenly imports app-specific constants | Breaks reuse contract for other consumers | Inject as prop or move constant to the shared package |

### Repetition / refactor candidates

| Trigger in diff | Check | What to flag |
|---|---|---|
| 3+ near-identical JSX blocks (social links, stat cards, fee rows, form fields) | Can they be generated by `.map()` over a config array? | Extract — readability and one-place-to-edit |
| Same 3-5 line validation / transform used in ≥2 places in the diff | Is it already a util? | Extract to a shared helper |
| Two naming styles for the same concept in the same PR (`PRIMARY_DIALOG_BUTTON_CLASS` vs `checkboxRowClass`) | Pick one — SCREAMING_CASE for constants, camelCase for locals | Consistency call-out |

---

## General principles (applied after the trigger pass)

These are reminders to keep in mind while reading the diff — they rarely justify a standalone finding on their own.

- **Code health** — would future devs be happy this exists? Complexity justified for **current** needs, not speculative future?
- **Every-line rule** — did you look at every non-generated line?
- **Integration** — does the change fit the surrounding system, or fight it?
- **Error paths** — null/undefined, empty collections, network failures, timeouts, cancellation on unmount.
- **Concurrency** — shared mutable state, race conditions, double-submit guards.

## Tests

- [ ] New code paths have corresponding tests (unit / integration / e2e as appropriate).
- [ ] Tests actually fail when the code is wrong — check for asserting on trivially-true outputs.
- [ ] Edge cases and failure modes covered.

## Documentation

- [ ] Public API / config / behavior changes → update the relevant README or doc.
- [ ] Stale docs matching deleted code → remove in the same PR.

---

## Frontend deep-dive (concise)

**Accessibility (WCAG 2.1 AA)** — semantic HTML (`header`/`main`/`nav`, not bare `div`), ARIA roles only when needed, form inputs have labels, keyboard nav works, color contrast ≥4.5:1 for text.

**Bundle & performance** — new heavy dep? Check bundle impact. New page? `lazy()` it. Large list? Virtualize.

**Monetary/financial data** — keep decimals as strings until display formatting; avoid float arithmetic on prices.

## Backend deep-dive (concise)

**Correctness** — idempotency keys on retry-safe endpoints; transactions for multi-step writes; optimistic/row locking for concurrent updates.

**Security** — input validated at entry; every protected endpoint checks authorization (not just authentication); parameterized queries only; error responses don't leak stack traces or internals.

**Resilience** — timeouts on all external calls; retry with backoff; rate limiting on public endpoints; graceful degradation.

**Observability** — useful logs at the right level; no PII in logs; correlation IDs for request tracing.

---

## Context-gathering strategy

When reviewing a diff, you lack full repo context. Search proactively when a trigger fires — don't rely on the diff alone:

- **Modified exports** — changed function/type signatures: grep all call sites and verify each one.
- **Ambient context** — if `auth.ts` changed, also read `middleware/auth.ts` and `__tests__/auth.test.ts`.
- **Monorepo neighbors** — if the change is in `apps/foo/`, check `packages/*` and `apps/bar/` for the same pattern.
- **Config sources** — if a token/helper is referenced, confirm it's defined in the project's token/theme/constants file.

---

## Change size guidance

**Ideal** ≤400 lines of meaningful change. **Effective maximum** ~1000 lines (beyond this, reviewer catch-rate drops ~75%).

If the diff is larger:

> **[Medium]** Large change (X lines). Consider splitting into logical PRs — core change, tests, docs/cleanup — for faster and safer review.

---

## Output format (per finding)

````
### N. Brief title

**File:** `path/to/file.ext:42` (or `:42-58` for a range)

**Issue:** Clear, specific explanation. Include what's wrong *and* the impact.

**Suggested fix:**
```lang
// Copy-paste ready code
```

**Why this matters:** One line on business/user impact.
````

**Rules:** every finding needs a `File:` with line number (range ok). Suggested code lives inside the markdown doc only — never edit source files unless the user explicitly asks. Priority-tag the title (`[Critical]` / `[High]` / `[Medium]` / `[Nit]`).

---

## Positive notes (always include a few)

Call out what was done well: elegant design, thoughtful abstractions, good test coverage, clear naming, accessibility forethought, performance care, security hardening, helpful comments. This keeps reviews honest and motivating.

---

## Further reading

- [Google: What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [Google: Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [Microsoft Research: Code Review Best Practices](https://www.michaelagreiler.com/code-reviews-at-microsoft-how-to-code-review-at-a-large-software-company/)
- [Meta Engineering: Fast Reviews](https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving-developer-experience/)
