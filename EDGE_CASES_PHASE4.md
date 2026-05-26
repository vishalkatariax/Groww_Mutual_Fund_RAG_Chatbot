# Edge Cases — Phase 4: Compliance, Safety & Guardrails

## Overview

This document catalogs all identified edge cases for Phase 4 of the Mutual Fund FAQ Assistant. Each edge case includes a description, expected behavior, and mitigation strategy.

---

## 1. Input Guardrail — PII Detection Edge Cases

### 1.1 — PAN Number Embedded in Natural Language

| Field | Detail |
|---|---|
| **Edge Case** | User types "My PAN is ABCDE1234F, what is the expense ratio of HDFC Mid-Cap Fund?" |
| **Trigger** | User volunteers personal information unprompted |
| **Impact** | PII logged in query history; potential privacy violation |
| **Expected Behavior** | Reject the entire query; warn user about PII; do not process the factual portion |
| **Mitigation** | PAN regex: `[A-Z]{5}[0-9]{4}[A-Z]`; if detected, respond: "For your security, please do not share personal information like PAN numbers. Please re-enter your question without any personal details."; log only that PII was detected (never log the PII value itself) |

### 1.2 — Aadhaar Number in Various Formats

| Field | Detail |
|---|---|
| **Edge Case** | User enters Aadhaar as "1234 5678 9012" or "1234-5678-9012" or "123456789012" |
| **Trigger** | Aadhaar entered with spaces, hyphens, or no separators |
| **Impact** | Regex may miss formatted Aadhaar numbers |
| **Expected Behavior** | All Aadhaar formats should be detected |
| **Mitigation** | Normalize input (strip spaces and hyphens) before regex check; pattern: `\d{12}` after normalization; if detected, reject query same as PAN |

### 1.3 — False Positive PII Detection

| Field | Detail |
|---|---|
| **Edge Case** | User asks "What is the NAV of HDFC Mid-Cap Fund at 1234567890?" where the number is not PII |
| **Trigger** | 12-digit numbers that look like Aadhaar but aren't |
| **Impact** | Legitimate queries blocked unnecessarily |
| **Expected Behavior** | Guardrail should have context-awareness for number patterns |
| **Mitigation** | Apply PII check only when numbers appear near PII-contextual keywords ("my PAN", "my Aadhaar", "my account"); if 12-digit number appears without PII context, flag for review but allow the query through; log flagged queries for manual audit |

### 1.4 — Email Address in Query

| Field | Detail |
|---|---|
| **Edge Case** | User types "Send details to john@example.com" |
| **Trigger** | User includes email in query |
| **Impact** | Email stored in logs |
| **Expected Behavior** | Strip the email from the query; process the remaining text |
| **Mitigation** | Email regex: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`; if found, strip it; process the cleaned query; log that email was stripped (not the email value) |

### 1.5 — Phone Number Ambiguity

| Field | Detail |
|---|---|
| **Edge Case** | User mentions "SIP of 10000" which could be confused with a phone number pattern |
| **Trigger** | 10-digit investment amounts or NAV values |
| **Impact** | SIP amounts incorrectly flagged as phone numbers |
| **Expected Behavior** | Only flag numbers that look like Indian mobile numbers (start with 6-9) |
| **Mitigation** | Indian mobile regex: `[6-9]\d{9}` (must start with 6-9); SIP amounts typically preceded by "₹", "Rs", or "INR"; only strip if pattern matches mobile format without currency prefix |

### 1.6 — OTP in Query

| Field | Detail |
|---|---|
| **Edge Case** | User types "My OTP is 456789, what is the exit load?" |
| **Trigger** | User shares OTP accidentally |
| **Impact** | Security breach; OTP exposure |
| **Expected Behavior** | Reject query immediately; warn user about OTP sharing |
| **Mitigation** | Detect 4-6 digit numbers near "OTP" keyword; if found, reject: "For your security, please never share OTPs. Please re-enter your question without any security codes."; critical severity — log and alert |

---

## 2. Input Guardrail — Topic Filter Edge Cases

### 2.1 — Off-Topic Query About Other Financial Products

| Field | Detail |
|---|---|
| **Edge Case** | User asks "What is the price of Bitcoin?" or "Should I buy gold?" |
| **Trigger** | Query about non-mutual-fund financial products |
| **Impact** | System processes an irrelevant query; wastes resources |
| **Expected Behavior** | Reject with a clear scope message |
| **Mitigation** | Topic filter checks for mutual-fund-related keywords: "mutual fund", "SIP", "NAV", "expense ratio", "exit load", "ELSS", etc.; if no MF keywords found, respond: "I can only answer factual questions about HDFC mutual fund schemes. I don't have information about other financial products." |

### 2.2 — Partially On-Topic Query

| Field | Detail |
|---|---|
| **Edge Case** | User asks "What is the tax benefit of ELSS vs PPF?" — ELSS is in scope, PPF is not |
| **Trigger** | Query spans in-scope and out-of-scope topics |
| **Impact** | System may attempt to answer about PPF (out of scope) |
| **Expected Behavior** | Answer the in-scope portion (ELSS tax benefits) only |
| **Mitigation** | If query contains both in-scope and out-of-scope topics, answer the in-scope part and note: "I only have information about mutual fund schemes. For PPF details, please check the relevant government resources." |

### 2.3 — Non-Financial Query

| Field | Detail |
|---|---|
| **Edge Case** | User asks "What is the weather today?" or "Tell me a joke" |
| **Trigger** | Completely off-topic input |
| **Impact** | Wasted processing |
| **Expected Behavior** | Polite refusal with scope reminder |
| **Mitigation** | If no financial keywords detected at all, respond: "I'm a mutual fund FAQ assistant. I can only answer factual questions about HDFC mutual fund schemes." |

---

## 3. Input Guardrail — Advisory Detector Edge Cases

### 3.1 — Indirect Advisory: "Is This Fund Safe?"

| Field | Detail |
|---|---|
| **Edge Case** | User asks "Is HDFC Mid-Cap Fund safe?" — not explicitly asking "should I invest" but seeking a judgment |
| **Trigger** | Advisory intent disguised as a factual-sounding question |
| **Impact** | LLM may respond with a subjective assessment of safety |
| **Expected Behavior** | Redirect to factual riskometer data; refuse the safety judgment |
| **Mitigation** | Detect advisory-coded words: "safe", "risky", "reliable", "trustworthy"; respond with factual data: "HDFC Mid-Cap Fund has a 'Very High Risk' riskometer rating as per SEBI guidelines. I cannot assess whether a fund is safe for you. Source: https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth" |

### 3.2 — Advisory With Factual Prefix

| Field | Detail |
|---|---|
| **Edge Case** | "I know the expense ratio is 1.03%, but should I invest?" |
| **Trigger** | User states a fact then asks for advice |
| **Impact** | Classifier may see the factual prefix and route to RAG |
| **Expected Behavior** | Route to refusal handler for the advisory portion |
| **Mitigation** | Intent classifier should evaluate the full query; if any part is advisory, route to refusal; respond: "I cannot provide investment advice. I can only share that the expense ratio of HDFC Mid-Cap Fund (Direct) is available on its Groww page." |

### 3.3 — Hypothetical Advisory

| Field | Detail |
|---|---|
| **Edge Case** | "If I invest 5000 per month in HDFC ELSS, how much will I get?" |
| **Trigger** | User asks for a return projection / calculation |
| **Impact** | Any projected number is speculative and constitutes advice |
| **Expected Behavior** | Refuse; direct to Groww for historical data only |
| **Mitigation** | Detect projection patterns: "how much will I get", "what will be the return", "if I invest X"; respond: "I cannot project future returns or calculate expected amounts. Past performance does not guarantee future results. You can view historical returns on the Groww scheme page." |

---

## 4. Output Guardrail Edge Cases

### 4.1 — LLM Generates Advisory Language Without Trigger Keywords

| Field | Detail |
|---|---|
| **Edge Case** | LLM says "This fund has consistently delivered strong returns" — advisory implication without explicit keywords like "recommend" or "should" |
| **Trigger** | LLM uses qualitative language about performance |
| **Impact** | Implied recommendation; compliance violation |
| **Expected Behavior** | Output guardrail should detect qualitative performance language |
| **Mitigation** | Expand advisory keyword list to include: "consistently delivered", "strong returns", "outperformed", "underperformed", "best performer", "top performing"; if detected, strip the sentence; regenerate with: "Do NOT use qualitative performance language. Only state factual data." |

### 4.2 — Source URL Points to Wrong Scheme Page

| Field | Detail |
|---|---|
| **Edge Case** | Response cites HDFC Mid-Cap Fund's Groww URL but the data is about HDFC Equity Fund |
| **Trigger** | LLM mixes up context from multiple schemes |
| **Impact** | User clicks source and sees different data; trust broken |
| **Expected Behavior** | Source URL must match the scheme discussed in the answer |
| **Mitigation** | After LLM generation, extract the scheme name from the answer; verify the source URL matches that scheme's Groww page; if mismatch, replace with correct URL from metadata; log mismatches |

### 4.3 — Response Contains No Source URL at All

| Field | Detail |
|---|---|
| **Edge Case** | LLM generates a factual answer but omits the source citation |
| **Trigger** | LLM doesn't follow the "include exactly ONE source" instruction |
| **Impact** | Response lacks transparency; violates core requirement |
| **Expected Behavior** | If no URL found, append the relevant Groww URL from context |
| **Mitigation** | Check for URL pattern in response; if missing, take the source_url from the highest-scoring retrieved chunk and append: "Source: {url}"; do not regenerate — just append |

### 4.4 — Response Length Exceeds 3 Sentences After All Processing

| Field | Detail |
|---|---|
| **Edge Case** | After appending source URL and "Last updated" footer, the total response exceeds 3 sentences |
| **Trigger** | Source URL and footer are counted as additional sentences |
| **Impact** | Technical violation of the 3-sentence rule |
| **Expected Behavior** | The 3-sentence limit applies to the factual answer only; source and footer are metadata |
| **Mitigation** | Define the response format clearly: `answer` (max 3 sentences) + `source_url` (separate field) + `last_updated` (separate field); sentence counting applies only to the `answer` field; in the API response, these are separate JSON fields, not concatenated |

### 4.5 — Disclaimer Not Appended to Refusal Responses

| Field | Detail |
|---|---|
| **Edge Case** | Advisory refusal response doesn't include the "Facts-only. No investment advice." disclaimer |
| **Trigger** | Refusal handler doesn't append the disclaimer |
| **Impact** | Missing regulatory disclaimer |
| **Expected Behavior** | All responses (both factual and refusal) should include the disclaimer |
| **Mitigation** | Output guardrail appends the disclaimer to every response type; the disclaimer is a constant string appended after the main response; validate in tests that disclaimer is always present |

---

## 5. Domain Allow-List Edge Cases

### 5.1 — Groww URL Contains Tracking Parameters

| Field | Detail |
|---|---|
| **Edge Case** | LLM generates a Groww URL with UTM parameters: `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth?utm_source=assistant` |
| **Trigger** | LLM adds tracking parameters from training data |
| **Impact** | URL still points to correct page; no functional issue |
| **Expected Behavior** | Strip tracking parameters; validate base URL |
| **Mitigation** | Parse URL; strip query parameters and fragments; validate only the base URL against allow-list; `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth` is valid regardless of query params |

### 5.2 — Shortened or Redirected Groww URL

| Field | Detail |
|---|---|
| **Edge Case** | LLM generates `https://groww.in/v/abc123` — a Groww short link |
| **Trigger** | LLM hallucinates a non-standard Groww URL format |
| **Impact** | URL may or may not be valid |
| **Expected Behavior** | Only allow the known 5 scheme page URLs |
| **Mitigation** | Maintain an explicit allow-list of the 5 known Groww URLs; any URL not in this list is rejected; replace with the correct known URL if the scheme can be identified; if scheme cannot be identified, return fallback message |

### 5.3 — HTTP vs HTTPS

| Field | Detail |
|---|---|
| **Edge Case** | LLM generates `http://groww.in/...` instead of `https://groww.in/...` |
| **Trigger** | Inconsistent URL scheme in LLM output |
| **Impact** | URL works but uses insecure protocol |
| **Expected Behavior** | All URLs should use HTTPS |
| **Mitigation** | Normalize all URLs to HTTPS before validation; if domain matches but scheme is HTTP, auto-upgrade to HTTPS |

---

## Edge Case Summary Table

| # | Edge Case | Severity | Phase Component | Auto-Recoverable |
|---|---|---|---|---|
| 1.1 | PAN in natural language | Critical | PII Detector | Yes (reject + warn) |
| 1.2 | Aadhaar in various formats | Critical | PII Detector | Yes (normalize + reject) |
| 1.3 | False positive PII | Medium | PII Detector | Partial (context-aware) |
| 1.4 | Email in query | Medium | PII Detector | Yes (strip + proceed) |
| 1.5 | Phone number vs SIP amount | Medium | PII Detector | Yes (mobile format check) |
| 1.6 | OTP in query | Critical | PII Detector | Yes (reject + warn) |
| 2.1 | Off-topic financial query | Low | Topic Filter | Yes (scope message) |
| 2.2 | Partially on-topic query | Medium | Topic Filter | Partial (answer in-scope only) |
| 2.3 | Non-financial query | Low | Topic Filter | Yes (scope message) |
| 3.1 | Indirect advisory ("is it safe?") | High | Advisory Detector | Yes (redirect to riskometer) |
| 3.2 | Advisory with factual prefix | High | Advisory Detector | Yes (split handling) |
| 3.3 | Hypothetical / projection query | High | Advisory Detector | Yes (refuse projection) |
| 4.1 | Subtle advisory language | High | Output Guard | Yes (expanded keyword list) |
| 4.2 | Source URL mismatch | High | Output Guard | Yes (URL correction) |
| 4.3 | Missing source URL | High | Output Guard | Yes (auto-append) |
| 4.4 | Sentence count with metadata | Medium | Output Guard | Yes (separate fields) |
| 4.5 | Missing disclaimer on refusals | Medium | Output Guard | Yes (auto-append) |
| 5.1 | URL with tracking parameters | Low | Domain Allow-List | Yes (strip params) |
| 5.2 | Shortened / unknown Groww URL | Medium | Domain Allow-List | Yes (explicit URL list) |
| 5.3 | HTTP vs HTTPS | Low | Domain Allow-List | Yes (normalize to HTTPS) |
