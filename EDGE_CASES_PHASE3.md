# Edge Cases — Phase 3: Retrieval & RAG Pipeline

## Overview

This document catalogs all identified edge cases for Phase 3 of the Mutual Fund FAQ Assistant. Each edge case includes a description, expected behavior, and mitigation strategy.

---

## 1. Query Pre-Processing Edge Cases

### 1.1 — Typos in Scheme Names

| Field | Detail |
|---|---|
| **Edge Case** | User types "HDFC midcap fund" instead of "HDFC Mid-Cap Fund" |
| **Trigger** | User query contains misspelled or abbreviated scheme names |
| **Impact** | Entity extraction fails; vector search retrieves wrong or no results |
| **Expected Behavior** | Pre-processor should normalize known scheme name variants |
| **Mitigation** | Maintain an alias mapping: `"hdfc midcap" → "HDFC Mid-Cap Fund"`, `"hdfc elss" → "HDFC ELSS Tax Saver Fund"`, etc.; use fuzzy matching (Levenshtein distance ≤ 2) against known scheme names; if no match found, proceed with original query |

### 1.2 — Query in Mixed Language (Hinglish)

| Field | Detail |
|---|---|
| **Edge Case** | User asks "HDFC mid-cap fund ka expense ratio kya hai?" |
| **Trigger** | Indian retail investors commonly mix Hindi and English |
| **Impact** | Embedding model may not align Hinglish with English corpus chunks |
| **Expected Behavior** | System should extract the factual intent and scheme name, ignoring the Hindi filler words |
| **Mitigation** | Strip common Hindi filler words ("ka", "kya", "hai", "ke", "mein", "se"); extract English keywords + scheme name; if > 50% non-English, log as Hinglish query; the embedding model (OpenAI) handles mixed-language reasonably well |

### 1.3 — Ambiguous Scheme Reference

| Field | Detail |
|---|---|
| **Edge Case** | User asks "What is the expense ratio of HDFC fund?" without specifying which HDFC scheme |
| **Trigger** | Query references AMC name but no specific scheme |
| **Impact** | Vector search returns chunks from multiple HDFC schemes; response is ambiguous |
| **Expected Behavior** | Assistant should ask the user to specify the scheme |
| **Mitigation** | If retrieved chunks come from > 2 different schemes and no single scheme dominates, respond: "I found multiple HDFC schemes. Could you specify which one? For example: HDFC Mid-Cap Fund, HDFC Equity Fund, HDFC Focused Fund, HDFC ELSS Tax Saver Fund, or HDFC Large Cap Fund." |

### 1.4 — Extremely Long Query

| Field | Detail |
|---|---|
| **Edge Case** | User pastes a paragraph-length query (e.g., "I have been investing in mutual funds for 3 years and I want to know what the current expense ratio is for the HDFC Mid-Cap Fund direct growth plan that I have been investing in through SIP...") |
| **Trigger** | User provides excessive context in their question |
| **Impact** | Query embedding gets diluted by irrelevant context; retrieval quality degrades |
| **Expected Behavior** | Pre-processor should extract the core factual question |
| **Mitigation** | Truncate queries > 200 tokens; extract the last sentence or the sentence containing a question mark as the core query; log long queries for analysis |

### 1.5 — Empty or Whitespace-Only Query

| Field | Detail |
|---|---|
| **Edge Case** | User submits an empty string or only whitespace |
| **Trigger** | Accidental form submission |
| **Impact** | Pipeline crashes on empty embedding input |
| **Expected Behavior** | Return a friendly message asking the user to enter a question |
| **Mitigation** | Validate query is non-empty and > 3 characters after trimming; if invalid, return: "Please enter a question about a mutual fund scheme." |

---

## 2. Intent Classifier Edge Cases

### 2.1 — Subtle Advisory Queries Disguised as Factual

| Field | Detail |
|---|---|
| **Edge Case** | "Is the expense ratio of HDFC Mid-Cap Fund too high?" — appears factual but contains subjective judgment ("too high") |
| **Trigger** | Query combines a factual element with an advisory qualifier |
| **Impact** | Intent classifier routes to RAG; LLM may inadvertently give an opinion |
| **Expected Behavior** | Classify as ADVISORY and refuse the subjective part; answer only the factual portion |
| **Mitigation** | Intent classifier should detect advisory qualifiers ("too high", "worth it", "good", "bad", "reasonable"); route to a hybrid handler: provide the factual data (expense ratio value) but refuse the advisory interpretation ("Whether 1.03% is too high depends on your investment goals. I can only confirm the expense ratio is 1.03%.") |

### 2.2 — Performance Comparison as Factual Query

| Field | Detail |
|---|---|
| **Edge Case** | "What is the 1-year return of HDFC Mid-Cap Fund vs HDFC Large Cap Fund?" — asks for factual data but implies comparison |
| **Trigger** | User asks for side-by-side return data |
| **Impact** | Per problem statement constraints, no performance comparisons should be provided |
| **Expected Behavior** | Provide links to both scheme pages on Groww without calculating or comparing |
| **Mitigation** | Intent classifier should detect comparison patterns ("vs", "compared to", "difference between"); route to a comparison handler that responds: "I cannot compare fund performance. You can find the returns for each scheme on their Groww pages: [link1] [link2]" |

### 2.3 — Query About a Scheme Not in Corpus

| Field | Detail |
|---|---|
| **Edge Case** | User asks "What is the expense ratio of SBI Bluechip Fund?" — a valid factual query about a scheme not covered |
| **Trigger** | Query references a scheme outside the 5 HDFC funds |
| **Impact** | Vector search returns irrelevant or low-confidence results |
| **Expected Behavior** | Respond that the scheme is not covered, listing the available schemes |
| **Mitigation** | After vector search, check if top results all have similarity < 0.4; if yes, and if the query mentions a scheme name not in the corpus, respond: "I only have information about the following HDFC schemes: HDFC Mid-Cap Fund, HDFC Equity Fund, HDFC Focused Fund, HDFC ELSS Tax Saver Fund, HDFC Large Cap Fund. Please ask about one of these." |

### 2.4 — Greeting / Small Talk

| Field | Detail |
|---|---|
| **Edge Case** | User says "Hi" or "Hello" or "How are you?" |
| **Trigger** | Non-query conversational input |
| **Impact** | Intent classifier may misclassify as AMBIGUOUS |
| **Expected Behavior** | Respond with a friendly greeting + prompt to ask a factual question |
| **Mitigation** | Add a GREETING intent class; respond: "Hello! I'm your Mutual Fund FAQ Assistant. Ask me factual questions about HDFC mutual fund schemes. For example: 'What is the expense ratio of HDFC Mid-Cap Fund?'" |

### 2.5 — Multi-Intent Query

| Field | Detail |
|---|---|
| **Edge Case** | User asks "What is the expense ratio and exit load of HDFC Mid-Cap Fund?" — two factual questions in one |
| **Trigger** | Compound question with "and" |
| **Impact** | LLM may answer only one part; response may exceed 3-sentence limit |
| **Expected Behavior** | Answer both factual parts concisely within 3 sentences |
| **Mitigation** | Prompt template should instruct: "If the query contains multiple factual questions, answer all parts concisely within the 3-sentence limit"; response validator should allow up to 4 sentences for multi-part questions (flag for review) |

---

## 3. Vector Search & Retrieval Edge Cases

### 3.1 — All Retrieved Chunks from Wrong Scheme

| Field | Detail |
|---|---|
| **Edge Case** | Query asks about HDFC Mid-Cap Fund but top-K chunks all belong to HDFC Large Cap Fund |
| **Trigger** | Schemes have similar content (e.g., similar expense ratio descriptions) |
| **Impact** | Wrong fund data in response |
| **Expected Behavior** | Context assembler should validate scheme alignment |
| **Mitigation** | After retrieval, check if > 60% of chunks belong to a single scheme; if the query mentions a different scheme name, filter chunks to match the requested scheme; if no chunks match, return the "not found" message |

### 3.2 — Retrieved Chunks Contradict Each Other

| Field | Detail |
|---|---|
| **Edge Case** | Top-5 chunks contain conflicting data (e.g., one chunk says expense ratio is 1.03%, another says 1.55% — direct vs regular plan) |
| **Trigger** | Same fund has different values for direct vs regular plan |
| **Impact** | LLM may hallucinate or pick one value arbitrarily |
| **Expected Behavior** | LLM should present both values with plan context |
| **Mitigation** | Prompt should instruct: "If multiple values exist (e.g., direct vs regular plan), present both clearly"; response validator should allow an extra sentence for plan-specific distinctions |

### 3.3 — Retrieved Chunks Are Insufficient to Answer

| Field | Detail |
|---|---|
| **Edge Case** | Top-K chunks are retrieved but none contain the specific information requested |
| **Trigger** | User asks about a detail not present on the Groww page (e.g., "What is the portfolio manager's name?") |
| **Impact** | LLM hallucinates an answer from insufficient context |
| **Expected Behavior** | LLM should decline to answer and direct user to Groww |
| **Mitigation** | Prompt instruction #4 already covers this: "If the context does not contain the answer, say: 'I could not find this information in the available scheme pages. Please check Groww directly.'"; additionally, response validator should check if the answer directly references the retrieved chunks |

### 3.4 — Query Matches Boilerplate Chunks

| Field | Detail |
|---|---|
| **Edge Case** | User asks about "market risks" and retrieves the boilerplate disclaimer from multiple scheme pages |
| **Trigger** | Boilerplate not fully removed during Phase 1 |
| **Impact** | Non-informative response; wasted Top-K slots |
| **Expected Behavior** | Boilerplate chunks should be deprioritized or filtered |
| **Mitigation** | Tag boilerplate chunks during ingestion (Phase 1) with `is_boilerplate: true` in metadata; during retrieval, filter out chunks where `is_boilerplate: true` unless no other results exist |

---

## 4. Prompt Builder Edge Cases

### 4.1 — Context Exceeds Token Budget

| Field | Detail |
|---|---|
| **Edge Case** | Top-K chunks with metadata exceed the 2048 token context budget |
| **Trigger** | Very detailed Groww pages produce large chunks |
| **Impact** | Prompt truncated; LLM receives incomplete context |
| **Expected Behavior** | Context assembler should truncate at chunk boundaries, not mid-text |
| **Mitigation** | Sum token counts of chunks; if > budget, remove the lowest-scoring chunk; repeat until within budget; log truncation events |

### 4.2 — Special Characters in User Query Break Prompt Formatting

| Field | Detail |
|---|---|
| **Edge Case** | User query contains `{`, `}`, `<`, `>`, or other characters that may interfere with prompt template placeholders |
| **Trigger** | User types: "What is the NAV of <HDFC Mid-Cap Fund>" |
| **Impact** | Prompt template breaks; LLM receives malformed input |
| **Expected Behavior** | User input should be sanitized before prompt injection |
| **Mitigation** | Escape special characters in user query before inserting into prompt template; wrap user query in a dedicated section marker; validate final prompt string before sending to LLM |

---

## 5. LLM Generator Edge Cases

### 5.1 — LLM Returns Empty Response

| Field | Detail |
|---|---|
| **Edge Case** | OpenAI API returns an empty string or null content |
| **Trigger** | API glitch or content filter triggered |
| **Impact** | User receives blank response |
| **Expected Behavior** | Retry the generation; if persists, return fallback message |
| **Mitigation** | If `response.content` is empty or None, retry with the same prompt (max 2 times); if still empty, return: "I'm unable to generate a response right now. Please try again." |

### 5.2 — LLM Response Exceeds 3 Sentences

| Field | Detail |
|---|---|
| **Edge Case** | LLM generates 4+ sentences despite the 3-sentence constraint in the prompt |
| **Trigger** | Complex context that the model tries to fully explain |
| **Impact** | Response violates the project's 3-sentence maximum rule |
| **Expected Behavior** | Response validator should truncate to 3 sentences |
| **Mitigation** | Response validator splits response by sentence boundaries (`.`, `!`, `?`); keeps only the first 3; appends "..." if truncated; log truncated responses for prompt tuning |

### 5.3 — LLM Hallucinates Source URL

| Field | Detail |
|---|---|
| **Edge Case** | LLM generates a source URL that doesn't match any of the 5 Groww URLs (e.g., fabricates `https://www.hdfcfund.com/...`) |
| **Trigger** | LLM relies on training data rather than the provided context |
| **Impact** | Invalid source citation; violates compliance requirement |
| **Expected Behavior** | Response validator should reject fabricated URLs |
| **Mitigation** | Response validator extracts URLs from the response; checks each against the known 5 Groww URLs; if URL not in allow-list, regenerate with stricter prompt: "You MUST use a source URL from the provided context only. Do NOT fabricate URLs."; max 2 retries |

### 5.4 — LLM Provides Investment Advice Despite Prompt

| Field | Detail |
|---|---|
| **Edge Case** | LLM generates advisory language like "This fund is a good choice for long-term investors" despite the explicit prohibition |
| **Trigger** | Context includes positive performance data that the model interprets as a recommendation |
| **Impact** | Compliance violation; advisory content served to user |
| **Expected Behavior** | Response validator should detect and strip advisory language |
| **Mitigation** | Output guardrail (Phase 4) catches this; advisory language filter checks for keywords: "good choice", "recommend", "should consider", "worth investing", "advisable", "beneficial"; if detected, strip the advisory sentence and regenerate; log all advisory leakage incidents |

### 5.5 — LLM API Timeout

| Field | Detail |
|---|---|
| **Edge Case** | OpenAI API takes > 30 seconds to respond |
| **Trigger** | API load spike or complex prompt |
| **Impact** | User waits too long; request may time out at the API gateway level |
| **Expected Behavior** | Implement timeout with fallback |
| **Mitigation** | Set 15-second timeout on LLM API call; if timeout, retry once; if second timeout, return: "I'm taking longer than expected to respond. Please try again."; log timeout frequency |

### 5.6 — LLM Returns Non-English Response

| Field | Detail |
|---|---|
| **Edge Case** | LLM responds in Hindi or another language (especially for Hinglish queries) |
| **Trigger** | User query contains Hindi words |
| **Impact** | Inconsistent user experience; may not be understood by all users |
| **Expected Behavior** | All responses should be in English |
| **Mitigation** | Add explicit instruction in system prompt: "Always respond in English, even if the query contains words from other languages."; if response is detected as non-English (> 50% non-ASCII characters), regenerate with explicit English instruction |

---

## 6. Response Validator Edge Cases

### 6.1 — Response Contains Multiple Source URLs

| Field | Detail |
|---|---|
| **Edge Case** | LLM includes two or more Groww URLs in the response |
| **Trigger** | Multi-scheme context or comparison-style answer |
| **Impact** | Violates the "exactly one citation link" rule |
| **Expected Behavior** | Keep only the most relevant source URL; remove others |
| **Mitigation** | Count URLs in response; if > 1, keep the first one (or the one matching the queried scheme); strip the others; log multi-URL responses |

### 6.2 — Response Missing "Last updated" Footer

| Field | Detail |
|---|---|
| **Edge Case** | LLM omits the "Last updated from sources: <date>" footer |
| **Trigger** | LLM doesn't follow the format instruction |
| **Impact** | Response doesn't meet the transparency requirement |
| **Expected Behavior** | Response validator should append the footer if missing |
| **Mitigation** | Check if response contains "Last updated from sources:"; if not, append it using the `scraped_date` from the retrieved chunk metadata; do not regenerate — just append |

### 6.3 — Response Contains Markdown or HTML Formatting

| Field | Detail |
|---|---|
| **Edge Case** | LLM returns response with `**bold**`, `<b>bold</b>`, or `[link](url)` formatting |
| **Trigger** | LLM uses formatting patterns from its training |
| **Impact** | Raw formatting characters shown to user in the chat interface |
| **Expected Behavior** | Strip markdown/HTML before sending to frontend; or render it properly |
| **Mitigation** | Strip markdown formatting (`**`, `*`, `##`, etc.); strip HTML tags; convert `[text](url)` to "text: url" plain text; the frontend SourceLink component handles URL display separately |

### 6.4 — All Validation Checks Fail

| Field | Detail |
|---|---|
| **Edge Case** | LLM response fails every validator check (too long, no source, advisory language, no footer) |
| **Trigger** | LLM completely ignores the system prompt |
| **Impact** | After 2 retries, system falls back to generic message |
| **Expected Behavior** | Return the fallback message without any LLM-generated content |
| **Mitigation** | After 2 failed retries, return: "I couldn't verify this information. Please check Groww directly."; log the original LLM response for debugging; do not expose raw LLM output to the user |

---

## Edge Case Summary Table

| # | Edge Case | Severity | Phase Component | Auto-Recoverable |
|---|---|---|---|---|
| 1.1 | Typos in scheme names | Medium | Query Pre-Processor | Yes (fuzzy matching) |
| 1.2 | Hinglish / mixed language | Medium | Query Pre-Processor | Partial (keyword extraction) |
| 1.3 | Ambiguous scheme reference | Medium | Query Pre-Processor | Yes (clarification prompt) |
| 1.4 | Extremely long query | Low | Query Pre-Processor | Yes (truncate / extract) |
| 1.5 | Empty / whitespace query | High | Query Pre-Processor | Yes (validation) |
| 2.1 | Subtle advisory in factual query | High | Intent Classifier | Partial (hybrid handler) |
| 2.2 | Performance comparison query | High | Intent Classifier | Yes (comparison handler) |
| 2.3 | Scheme not in corpus | Medium | Intent Classifier | Yes (list available schemes) |
| 2.4 | Greeting / small talk | Low | Intent Classifier | Yes (greeting intent) |
| 2.5 | Multi-intent query | Medium | Intent Classifier | Yes (multi-part answer) |
| 3.1 | Wrong scheme in results | High | Vector Search | Yes (scheme filter) |
| 3.2 | Contradictory chunks | Medium | Context Assembler | Yes (present both values) |
| 3.3 | Insufficient context to answer | Medium | Context Assembler | Yes (decline to answer) |
| 3.4 | Boilerplate chunks retrieved | Medium | Vector Search | Yes (metadata filter) |
| 4.1 | Context exceeds token budget | Medium | Prompt Builder | Yes (truncate lowest-scored) |
| 4.2 | Special chars break prompt | Medium | Prompt Builder | Yes (input sanitization) |
| 5.1 | LLM returns empty response | High | LLM Generator | Yes (retry + fallback) |
| 5.2 | Response exceeds 3 sentences | High | Response Validator | Yes (truncate) |
| 5.3 | LLM hallucinates source URL | Critical | Response Validator | Yes (URL allow-list check) |
| 5.4 | LLM provides investment advice | Critical | Response Validator | Yes (advisory filter) |
| 5.5 | LLM API timeout | Medium | LLM Generator | Yes (retry + fallback) |
| 5.6 | Non-English response | Low | Response Validator | Yes (regenerate in English) |
| 6.1 | Multiple source URLs | Medium | Response Validator | Yes (keep first, strip rest) |
| 6.2 | Missing "Last updated" footer | Medium | Response Validator | Yes (auto-append) |
| 6.3 | Markdown / HTML in response | Low | Response Validator | Yes (strip formatting) |
| 6.4 | All validation checks fail | Critical | Response Validator | Yes (fallback message) |
