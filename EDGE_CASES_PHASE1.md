# Edge Cases — Phase 1: Corpus Collection & Data Ingestion

## Overview

This document catalogs all identified edge cases for Phase 1 of the Mutual Fund FAQ Assistant. Each edge case includes a description, expected behavior, and mitigation strategy.

---

## 1. Web Scraping Edge Cases

### 1.1 — Groww Page Structure Variation

| Field | Detail |
|---|---|
| **Edge Case** | Different Groww scheme pages may have different HTML structures (e.g., missing sections, reordered elements, different CSS class names) |
| **Trigger** | Scraping any of the 5 URLs where Groww has updated the page layout |
| **Impact** | HTML-to-Text converter may miss sections or extract garbled content |
| **Expected Behavior** | Scraper should detect structural anomalies and log a warning |
| **Mitigation** | Use multiple CSS selector fallbacks; validate extracted text length > minimum threshold (e.g., 500 chars); flag pages with < 50% of expected sections for manual review |

### 1.2 — Dynamic / JavaScript-Rendered Content

| Field | Detail |
|---|---|
| **Edge Case** | Groww pages may render key data (expense ratio, NAV, holdings) via JavaScript after initial page load |
| **Trigger** | Using `requests` instead of a headless browser |
| **Impact** | Critical financial data missing from scraped content |
| **Expected Behavior** | Scraper should use Playwright with `wait_for_selector` to ensure JS-rendered content is captured |
| **Mitigation** | Primary scraper = Playwright with a 10s timeout; fallback to `requests` only for static content; compare text length between Playwright and `requests` output — if delta > 30%, flag as JS-dependent |

### 1.3 — Groww Rate Limiting / Blocking

| Field | Detail |
|---|---|
| **Edge Case** | Rapid successive requests to Groww may trigger rate limiting (HTTP 429) or IP blocking |
| **Trigger** | Scraping all 5 URLs in quick succession without delays |
| **Impact** | Incomplete corpus — some pages not scraped |
| **Expected Behavior** | Scraper should respect rate limits with exponential backoff |
| **Mitigation** | Add 5–10 second delay between requests; implement retry with backoff (3 retries, 2^n seconds); log HTTP status codes; if 429 received, pause for 60s before retry |

### 1.4 — Groww Page Returns 404 or Redirect

| Field | Detail |
|---|---|
| **Edge Case** | A Groww scheme URL may return 404, or redirect to a different URL (e.g., scheme merged/renamed) |
| **Trigger** | HDFC merges or renames a fund, Groww updates the URL |
| **Impact** | Missing scheme data in corpus |
| **Expected Behavior** | Scraper should detect non-200 responses and log an error |
| **Mitigation** | Validate HTTP 200 before processing; follow redirects but log the final URL; if 404, alert immediately — do not silently skip; maintain a URL health check report |

### 1.5 — Groww Page Contains Stale / Outdated Data

| Field | Detail |
|---|---|
| **Edge Case** | Groww may show outdated expense ratios or NAV that doesn't match the latest HDFC AMC factsheet |
| **Trigger** | Groww hasn't synced with the latest AMC data |
| **Impact** | Incorrect factual answers served to users |
| **Expected Behavior** | System should note the `last_updated` date from Groww page and include it in metadata |
| **Mitigation** | Extract and store the "as of" date from Groww pages; flag data older than 30 days; the `last_verified_date` field in the schema tracks when data was last confirmed |

### 1.6 — Cookie Consent / Login Wall

| Field | Detail |
|---|---|
| **Edge Case** | Groww may show a cookie consent popup or partial login wall that blocks content access |
| **Trigger** | First-time visit to a Groww page via headless browser |
| **Impact** | Scraper captures consent dialog HTML instead of scheme data |
| **Expected Behavior** | Playwright should dismiss cookie consent before scraping |
| **Mitigation** | Auto-accept cookie banners; wait for content container to be visible before extracting; validate that extracted text contains expected keywords (e.g., "expense ratio", "NAV") |

---

## 2. HTML-to-Text Conversion Edge Cases

### 2.1 — Tabular Data Loss

| Field | Detail |
|---|---|
| **Edge Case** | Groww displays fund details in HTML tables (e.g., fee structure, riskometer). BeautifulSoup may flatten tables into unstructured text |
| **Trigger** | Parsing pages with `<table>` elements containing expense ratio, exit load, etc. |
| **Impact** | Table relationships lost — expense ratio separated from its label |
| **Expected Behavior** | Tables should be converted to structured key-value pairs |
| **Mitigation** | Use table-aware extraction: iterate `<tr>` rows, map `<th>` to `<td>`; preserve table as "Label: Value" format; flag chunks containing table remnants for manual review |

### 2.2 — Unicode / Special Characters

| Field | Detail |
|---|---|
| **Edge Case** | Groww pages may contain special characters (₹, %, →, •, non-breaking spaces `&nbsp;`) that produce garbled text |
| **Trigger** | Parsing pages with rich formatting |
| **Impact** | Embeddings generate poor vectors for garbled text; retrieval quality degrades |
| **Expected Behavior** | All special characters should be normalized or preserved correctly |
| **Mitigation** | Run `BeautifulSoup.get_text(strip=True)` + Unicode normalization (NFKC); replace `&nbsp;` with space; map ₹ to "INR" or keep as-is consistently; validate output is valid UTF-8 |

### 2.3 — Empty or Near-Empty Pages

| Field | Detail |
|---|---|
| **Edge Case** | A Groww page may return valid HTML but with minimal content (e.g., "Coming soon" or error state) |
| **Trigger** | New fund launch where Groww hasn't populated the page yet |
| **Impact** | Empty documents enter the corpus, polluting vector search results |
| **Expected Behavior** | Pages with < 500 characters of clean text should be rejected |
| **Mitigation** | Add minimum content length check (500 chars); log rejected pages; do not create vector store entries for empty documents |

### 2.4 — Duplicate Content Across Pages

| Field | Detail |
|---|---|
| **Edge Case** | Groww may include boilerplate text (e.g., "Mutual fund investments are subject to market risks...") on every scheme page |
| **Trigger** | Scraping multiple Groww scheme pages |
| **Impact** | Vector search returns boilerplate chunks instead of scheme-specific data |
| **Expected Behavior** | Boilerplate sections should be identified and excluded from the corpus |
| **Mitigation** | Maintain a list of known boilerplate phrases; strip common disclaimers/footers; compare chunks across pages — if > 80% text overlap, flag as boilerplate |

---

## 3. Source Validation Edge Cases

### 3.1 — URL Redirects to Non-Groww Domain

| Field | Detail |
|---|---|
| **Edge Case** | A Groww URL may redirect to a different domain (e.g., cdn.groww.in, or an external partner) |
| **Trigger** | Groww implements CDN-based page serving |
| **Impact** | Source validator rejects the page because domain doesn't match `groww.in` |
| **Expected Behavior** | Allow redirects within groww.in subdomains; reject external domain redirects |
| **Mitigation** | Expand domain allow-list to `groww.in` + `*.groww.in`; log all redirects; reject if final domain is outside Groww ecosystem |

### 3.2 — HTTPS / SSL Issues

| Field | Detail |
|---|---|
| **Edge Case** | Groww may have SSL certificate issues or mixed content warnings |
| **Trigger** | Network-level SSL verification failure |
| **Impact** | Scraper fails to connect; no data retrieved |
| **Expected Behavior** | Log SSL errors; do not silently bypass certificate verification |
| **Mitigation** | Use `verify=True` in requests; if SSL fails, log and retry once; never disable SSL verification in production |

---

## 4. Metadata Tagging Edge Cases

### 4.1 — Scheme Name Mismatch

| Field | Detail |
|---|---|
| **Edge Case** | Groww may display a slightly different scheme name than the official HDFC AMC name (e.g., "HDFC Mid-Cap Opportunities Fund" vs "HDFC Mid-Cap Fund") |
| **Trigger** | Scraping page where Groww uses an abbreviated or alternate name |
| **Impact** | Metadata `scheme_name` inconsistent with user queries; retrieval fails |
| **Expected Behavior** | Use the canonical HDFC AMC scheme name in metadata, with Groww display name as alias |
| **Mitigation** | Maintain a mapping table: `{ groww_name: canonical_name }`; store both names in metadata; entity extraction during query time should match against both |

### 4.2 — Missing Category Information

| Field | Detail |
|---|---|
| **Edge Case** | Groww may not explicitly label the fund category (e.g., "Mid-Cap", "ELSS") in a machine-readable way |
| **Trigger** | Parsing pages where category is only implied by the fund name |
| **Impact** | `category` field in metadata is empty or incorrect |
| **Expected Behavior** | Category should be inferred from the scheme name if not explicitly available |
| **Mitigation** | Rule-based category inference: if "ELSS" in name → "elss"; if "Large Cap" → "large_cap"; if "Mid-Cap" → "mid_cap"; if "Focused" → "focused"; if "Equity" → "flexi_cap"; log when inference is used vs explicit label |

### 4.3 — Scraped Date Ambiguity

| Field | Detail |
|---|---|
| **Edge Case** | Groww pages may not show a clear "last updated" timestamp, or may show multiple dates (e.g., NAV date vs factsheet date) |
| **Trigger** | Parsing pages with ambiguous date fields |
| **Impact** | `scraped_date` and `last_verified_date` may be misleading |
| **Expected Behavior** | `scraped_date` = date the scraper ran (always known); `last_verified_date` = date shown on Groww page (if available) |
| **Mitigation** | Always set `scraped_date` to the scraper execution date; try to extract the data freshness date from Groww; if not found, mark `last_verified_date` as null and flag for manual verification |

---

## 5. Data Storage Edge Cases

### 5.1 — Large Page Content Exceeds Storage Limits

| Field | Detail |
|---|---|
| **Edge Case** | A single Groww scheme page may contain extensive data (holdings, historical performance tables) exceeding typical document size |
| **Trigger** | Scraping a page with detailed portfolio holdings (100+ rows) |
| **Impact** | JSON/Parquet files become very large; downstream chunking must handle large documents |
| **Expected Behavior** | No hard size limit, but content should be cleaned to remove unnecessary data |
| **Mitigation** | Strip navigation, footer, ads, and non-scheme content before storage; store `content_raw` (full) and `content_clean` (stripped); if `content_clean` > 100KB, log a warning |

### 5.2 — Concurrent Scraping Conflicts

| Field | Detail |
|---|---|
| **Edge Case** | Running the scraper multiple times simultaneously may cause write conflicts to the data store |
| **Trigger** | Manual scraper run while a scheduled run is in progress |
| **Impact** | Corrupted or partially written data files |
| **Expected Behavior** | Only one scraper instance should run at a time |
| **Mitigation** | Implement file-based lock (e.g., `.scraper.lock`); if lock exists and < 30 minutes old, abort; if lock exists and > 30 minutes old, consider it stale and override; log all scraping runs with timestamps |

---

## Edge Case Summary Table

| # | Edge Case | Severity | Phase Component | Auto-Recoverable |
|---|---|---|---|---|
| 1.1 | Page structure variation | Medium | Web Scraper | Partial (fallback selectors) |
| 1.2 | JS-rendered content | High | Web Scraper | Yes (Playwright) |
| 1.3 | Rate limiting / blocking | High | Web Scraper | Yes (backoff + retry) |
| 1.4 | 404 / redirect | High | Web Scraper | No (manual intervention) |
| 1.5 | Stale / outdated data | Medium | Source Validator | No (alert only) |
| 1.6 | Cookie consent wall | Medium | Web Scraper | Yes (auto-dismiss) |
| 2.1 | Tabular data loss | High | HTML-to-Text | Yes (table-aware parser) |
| 2.2 | Unicode / special chars | Low | HTML-to-Text | Yes (normalization) |
| 2.3 | Empty / near-empty pages | High | Source Validator | Yes (reject) |
| 2.4 | Duplicate / boilerplate | Medium | HTML-to-Text | Yes (dedup) |
| 3.1 | URL redirects off-domain | Medium | Source Validator | Yes (subdomain allow) |
| 3.2 | SSL / HTTPS issues | Low | Web Scraper | No (alert only) |
| 4.1 | Scheme name mismatch | Medium | Metadata Tagger | Yes (mapping table) |
| 4.2 | Missing category | Low | Metadata Tagger | Yes (rule inference) |
| 4.3 | Date ambiguity | Low | Metadata Tagger | Partial (use scrape date) |
| 5.1 | Large page content | Low | Data Storage | Yes (content stripping) |
| 5.2 | Concurrent scraping | Medium | Data Storage | Yes (file lock) |
