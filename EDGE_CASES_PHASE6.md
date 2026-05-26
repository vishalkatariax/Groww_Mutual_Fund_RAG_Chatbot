# Edge Cases — Phase 6: Frontend & User Interface

## Overview

This document catalogs all identified edge cases for Phase 6 of the Mutual Fund FAQ Assistant. Each edge case includes a description, expected behavior, and mitigation strategy.

---

## 1. Chat Interface Edge Cases

### 1.1 — User Sends Message While Previous Response Is Loading

| Field | Detail |
|---|---|
| **Edge Case** | User types and sends a new query before the previous response has returned |
| **Trigger** | Impatient user or slow network |
| **Impact** | Race condition — two concurrent API calls; responses may arrive out of order |
| **Expected Behavior** | Disable the input bar while a response is pending; or cancel the previous request |
| **Mitigation** | Disable send button and input during loading state; if using streaming, abort previous request on new send; display responses in order of query submission; use AbortController to cancel in-flight fetch requests |

### 1.2 — Browser Back/Forward Button During Chat

| Field | Detail |
|---|---|
| **Edge Case** | User presses browser back button while on the chat page |
| **Trigger** | Natural browser navigation |
| **Impact** | Chat history lost; page navigates away |
| **Expected Behavior** | Chat state should be preserved or a warning shown |
| **Mitigation** | Since the app is a single-page chat, prevent navigation away with `beforeunload` event if chat has messages; alternatively, persist chat history to `sessionStorage` so it survives back/forward navigation; restore chat on page revisit |

### 1.3 — Page Refresh Loses Chat History

| Field | Detail |
|---|---|
| **Edge Case** | User refreshes the page and all previous messages are gone |
| **Trigger** | Accidental refresh or browser crash |
| **Impact** | Poor user experience; user must re-ask questions |
| **Expected Behavior** | Chat history should survive page refresh within the same session |
| **Mitigation** | Store chat messages in `sessionStorage` (cleared on tab close, persists across refresh); on component mount, restore messages from storage; limit stored messages to last 50 to prevent storage overflow |

### 1.4 — Rapid Clicking on Example Question Chips

| Field | Detail |
|---|---|
| **Edge Case** | User clicks multiple example question chips in quick succession |
| **Trigger** | User exploring the interface |
| **Impact** | Multiple API requests fired; race condition on responses |
| **Expected Behavior** | Only the last clicked question should be processed |
| **Mitigation** | Debounce chip clicks (300ms); disable all chips while a response is pending; same mechanism as the input bar loading state |

### 1.5 — User Pastes Very Long Text into Input

| Field | Detail |
|---|---|
| **Edge Case** | User pastes 5000+ characters into the input field |
| **Trigger** | Copy-paste from another source |
| **Impact** | API rejects with 422 (max 1000 chars); confusing UX |
| **Expected Behavior** | Input field should show character limit and prevent submission if exceeded |
| **Mitigation** | Add character counter below input (e.g., "847/1000"); disable send button when > 1000 characters; show warning color (red) when approaching limit; auto-truncate with tooltip if needed |

### 1.6 — User Submits Query with Only Emojis or Special Characters

| Field | Detail |
|---|---|
| **Edge Case** | User types "📊💰" or "!!!" as their query |
| **Trigger** | Accidental or testing input |
| **Impact** | Backend processes a meaningless query; vector search returns irrelevant results |
| **Expected Behavior** | Frontend should validate that the query contains at least some alphabetic characters |
| **Mitigation** | Client-side validation: query must contain at least 3 alphabetic characters after stripping emojis/symbols; if invalid, show inline error: "Please enter a valid question about a mutual fund scheme." |

---

## 2. API Integration Edge Cases

### 2.1 — Backend Is Unreachable (Network Error)

| Field | Detail |
|---|---|
| **Edge Case** | Frontend cannot connect to the backend API (server down, network issues) |
| **Trigger** | Backend not started, server crash, or network disconnection |
| **Impact** | User sees no response; no feedback |
| **Expected Behavior** | Show a clear error message indicating connection issues |
| **Mitigation** | Catch `fetch` network errors; display: "Unable to connect to the server. Please check your internet connection and try again."; add a retry button; do not show raw error messages like "TypeError: Failed to fetch" |

### 2.2 — Backend Returns 500 Internal Server Error

| Field | Detail |
|---|---|
| **Edge Case** | API returns 500 due to an unexpected backend error |
| **Trigger** | ChromaDB crash, LLM API failure, unhandled exception |
| **Impact** | User sees no response or generic error |
| **Expected Behavior** | Show a user-friendly error; do not expose 500 details |
| **Mitigation** | Catch 5xx responses; display: "Something went wrong on our end. Please try again in a moment."; log the error details client-side for debugging; do not show stack traces or technical error messages |

### 2.3 — Backend Returns 429 Rate Limited

| Field | Detail |
|---|---|
| **Edge Case** | API returns 429 because the user has exceeded the rate limit |
| **Trigger** | Rapid repeated queries |
| **Impact** | User doesn't understand why their query was rejected |
| **Expected Behavior** | Show a clear message with when they can retry |
| **Mitigation** | Parse `Retry-After` header from 429 response; display: "You're sending questions too quickly. Please wait {N} seconds and try again."; disable the input for the cooldown period |

### 2.4 — API Response Takes > 10 Seconds

| Field | Detail |
|---|---|
| **Edge Case** | LLM generation takes > 10 seconds; user sees a frozen interface |
| **Trigger** | Complex query or slow LLM API |
| **Impact** | User thinks the app is broken; may refresh or leave |
| **Expected Behavior** | Show a typing indicator / loading animation; offer to cancel |
| **Mitigation** | Display animated dots ("...") in the bot message area while waiting; set a 30-second client-side timeout; if exceeded, show: "This is taking longer than expected. Would you like to try again?"; add a cancel button that aborts the fetch request |

### 2.5 — API Returns Unexpected Response Format

| Field | Detail |
|---|---|
| **Edge Case** | API returns valid JSON but missing expected fields (e.g., no `source_url`) |
| **Trigger** | Backend version mismatch or bug |
| **Impact** | Frontend crashes trying to render undefined fields |
| **Expected Behavior** | Frontend should handle missing fields gracefully |
| **Mitigation** | Use TypeScript interfaces with optional fields; provide default values: `source_url: response.source_url ?? null`; render conditionally — if `source_url` is null, don't show the source link component; log missing fields to console for debugging |

---

## 3. Display & Rendering Edge Cases

### 3.1 — Source URL Not Clickable on Mobile

| Field | Detail |
|---|---|
| **Edge Case** | Source URL displayed as plain text instead of a clickable link on mobile browsers |
| **Trigger** | CSS or HTML rendering issue on mobile |
| **Impact** | User cannot verify the source; transparency requirement violated |
| **Expected Behavior** | Source URL should always be a clickable `<a>` tag |
| **Mitigation** | Use `<a href={url} target="_blank" rel="noopener noreferrer">` for source links; add `color: blue; text-decoration: underline;` styling; test on iOS Safari and Android Chrome; ensure touch target is at least 44x44px |

### 3.2 — Very Long Source URL Breaks Layout

| Field | Detail |
|---|---|
| **Edge Case** | Groww URLs are ~60+ characters long and may overflow the chat bubble on narrow screens |
| **Trigger** | Mobile viewport with long URL |
| **Impact** | Horizontal scroll or broken layout |
| **Expected Behavior** | URLs should wrap or truncate gracefully |
| **Mitigation** | Use `word-break: break-all` or `overflow-wrap: break-word` for URL text; or display URL as "View Source →" link text instead of the raw URL; set `max-width` on message bubbles with `overflow: hidden` |

### 3.3 — "Last Updated" Date Shows Future Date

| Field | Detail |
|---|---|
| **Edge Case** | The `last_updated` field shows a date in the future due to timezone or scraping issues |
| **Trigger** | Backend returns incorrect date |
| **Impact** | Confusing or misleading information |
| **Expected Behavior** | Validate the date is not in the future |
| **Mitigation** | Frontend validates: if `last_updated > current_date`, display "Date unavailable" instead; log the anomaly; backend should also validate dates before sending |

### 3.4 — Refusal Response Styled Same as Factual Response

| Field | Detail |
|---|---|
| **Edge Case** | Advisory refusal looks identical to a factual answer |
| **Trigger** | Missing visual distinction in the frontend |
| **Impact** | User may not realize their question was refused; may misinterpret refusal as an answer |
| **Expected Behavior** | Refusal responses should have a distinct visual style (info/warning) |
| **Mitigation** | Use `is_refusal: true` from API response; render refusal messages with an info icon and light yellow/blue background; add "This question is outside my scope" prefix; factual answers use neutral styling |

### 3.5 — Disclaimer Banner Obscures Content on Small Screens

| Field | Detail |
|---|---|
| **Edge Case** | The sticky disclaimer banner takes too much vertical space on mobile devices |
| **Trigger** | Small viewport (e.g., iPhone SE, 375px width) |
| **Impact** | Limited chat area visible; poor usability |
| **Expected Behavior** | Disclaimer should be compact on mobile |
| **Mitigation** | Full text on desktop: "Facts-only. No investment advice."; Abbreviated on mobile: "Facts-only. No advice."; Use responsive font size and padding; consider a collapsible banner that auto-collapses after 5 seconds on mobile |

### 3.6 — Dark Mode / System Theme Mismatch

| Field | Detail |
|---|---|
| **Edge Case** | User's system is in dark mode but the app only supports light theme |
| **Trigger** | OS-level dark mode preference |
| **Impact** | Jarring visual experience; text may be hard to read |
| **Expected Behavior** | App should either support dark mode or force light mode |
| **Mitigation** | For v1, force light mode with `<html data-theme="light">` and CSS override; log dark mode as a future enhancement; ensure all text has explicit color (not inherited from system) |

---

## 4. Accessibility Edge Cases

### 4.1 — Screen Reader Cannot Distinguish User vs Bot Messages

| Field | Detail |
|---|---|
| **Edge Case** | Screen reader reads all messages as flat text without indicating who said what |
| **Trigger** | User using VoiceOver, NVDA, or other screen reader |
| **Impact** | Inaccessible; user cannot follow the conversation |
| **Expected Behavior** | Messages should have ARIA labels indicating sender |
| **Mitigation** | Add `aria-label="You: {message}"` for user messages; add `aria-label="Assistant: {message}"` for bot messages; use `role="log"` on the chat container; ensure new messages are announced via `aria-live="polite"` |

### 4.2 — Keyboard Navigation to Input Bar

| Field | Detail |
|---|---|
| **Edge Case** | User cannot Tab to the input field or send button |
| **Trigger** | Missing focus states or tab order |
| **Impact** | Inaccessible for keyboard-only users |
| **Expected Behavior** | All interactive elements should be keyboard-accessible |
| **Mitigation** | Ensure proper tab order: input → send button → example chips; add visible focus outlines (`:focus-visible`); Enter key should submit the query; Shift+Enter should insert a new line (if multi-line input is supported) |

---

## 5. Build & Deployment Edge Cases

### 5.1 — Frontend Build Fails Due to TypeScript Errors

| Field | Detail |
|---|---|
| **Edge Case** | Vite build fails with TypeScript compilation errors |
| **Trigger** | Type mismatch between API response interface and actual usage |
| **Impact** | Cannot deploy; CI/CD pipeline breaks |
| **Expected Behavior** | TypeScript errors should be caught in development, not in CI |
| **Mitigation** | Run `tsc --noEmit` as a pre-build step; fix all type errors before committing; use strict TypeScript config (`"strict": true`); add TypeScript check to CI pipeline before build step |

### 5.2 — Frontend Served from Different Domain Than Backend

| Field | Detail |
|---|---|
| **Edge Case** | Frontend deployed on `app.example.com` and backend on `api.example.com` |
| **Trigger** | Production deployment with separate domains |
| **Impact** | CORS issues; API calls blocked by browser |
| **Expected Behavior** | Backend should allow the frontend's origin in CORS |
| **Mitigation** | Configure `API_CORS_ORIGINS` in backend `.env` to include the frontend domain; use Nginx reverse proxy to serve both from the same domain in production (frontend: `/`, backend: `/api/*`); test CORS in staging before production deploy |

---

## Edge Case Summary Table

| # | Edge Case | Severity | Phase Component | Auto-Recoverable |
|---|---|---|---|---|
| 1.1 | Send while response loading | Medium | Chat Interface | Yes (disable input / abort) |
| 1.2 | Browser back/forward | Low | Chat Interface | Yes (sessionStorage) |
| 1.3 | Page refresh loses history | Medium | Chat Interface | Yes (sessionStorage) |
| 1.4 | Rapid chip clicking | Low | Chat Interface | Yes (debounce) |
| 1.5 | Very long input paste | Medium | Chat Interface | Yes (character limit) |
| 1.6 | Emojis / special chars only | Low | Chat Interface | Yes (validation) |
| 2.1 | Backend unreachable | High | API Integration | Yes (error message + retry) |
| 2.2 | Backend 500 error | High | API Integration | Yes (user-friendly error) |
| 2.3 | Rate limited (429) | Medium | API Integration | Yes (cooldown message) |
| 2.4 | API timeout > 10s | Medium | API Integration | Yes (loading + cancel) |
| 2.5 | Unexpected response format | Medium | API Integration | Yes (default values) |
| 3.1 | Source URL not clickable on mobile | Medium | Display | Yes (proper `<a>` tag) |
| 3.2 | Long URL breaks layout | Medium | Display | Yes (word-break / truncation) |
| 3.3 | Future date in last_updated | Low | Display | Yes (validate date) |
| 3.4 | Refusal same style as factual | Medium | Display | Yes (conditional styling) |
| 3.5 | Disclaimer obscures mobile view | Low | Display | Yes (responsive / collapsible) |
| 3.6 | Dark mode mismatch | Low | Display | Yes (force light theme) |
| 4.1 | Screen reader accessibility | Medium | Accessibility | No (code change needed) |
| 4.2 | Keyboard navigation | Medium | Accessibility | No (code change needed) |
| 5.1 | TypeScript build errors | High | Build | No (fix errors) |
| 5.2 | Cross-origin deployment | High | Deployment | Yes (CORS + proxy) |
