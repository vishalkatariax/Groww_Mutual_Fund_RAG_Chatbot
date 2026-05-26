"""
Web scraper for Groww scheme pages.

Uses Playwright to scrape JavaScript-rendered content from Groww URLs.
Implements rate limiting, retries with exponential backoff, and cookie handling.
"""

import logging
import time
from datetime import date
from typing import Optional

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

from config import GROWW_SCHEMES, settings
from app.guardrails.domain_allowlist import validate_is_groww, normalize_url

logger = logging.getLogger(__name__)


class GrowwScraper:
    """Scraper for Groww mutual fund scheme pages."""

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start(self):
        """Initialize Playwright browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        logger.info("Playwright browser initialized")

    def close(self):
        """Close browser and Playwright."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed")

    def scrape_all_schemes(self) -> list[dict]:
        """
        Scrape all 5 Groww scheme pages.

        Implements delay between requests to respect rate limits.

        Returns:
            List of scraped document dictionaries.
        """
        results = []

        for i, scheme in enumerate(GROWW_SCHEMES):
            if i > 0:
                logger.info(
                    f"Waiting {settings.scraping_delay}s before next request..."
                )
                time.sleep(settings.scraping_delay)

            logger.info(f"Scraping: {scheme['scheme_name']} ({scheme['url']})")

            try:
                doc = self.scrape_url(scheme["url"])
                if doc:
                    results.append(doc)
                    logger.info(f"✓ Successfully scraped: {scheme['scheme_name']}")
                else:
                    logger.warning(f"✗ Failed to scrape: {scheme['scheme_name']}")

            except Exception as e:
                logger.error(
                    f"✗ Error scraping {scheme['scheme_name']}: {e}",
                    exc_info=True,
                )

        logger.info(f"Scraping complete: {len(results)}/{len(GROWW_SCHEMES)} succeeded")
        return results

    def scrape_url(self, url: str) -> Optional[dict]:
        """
        Scrape a single Groww URL with retries.

        Args:
            url: The Groww scheme page URL.

        Returns:
            Dictionary with 'url', 'html', and 'scraped_date', or None on failure.
        """
        # Validate domain
        if not validate_is_groww(url):
            logger.error(f"URL not from Groww: {url}")
            return None

        normalized = normalize_url(url)

        for attempt in range(1, settings.scraping_max_retries + 1):
            try:
                page = self.context.new_page()

                # Set timeout for page load
                page.set_default_timeout(settings.scraping_timeout * 1000)

                # Navigate to page
                logger.info(f"  Attempt {attempt}: Loading {normalized}...")
                response = page.goto(normalized, wait_until="networkidle")

                # Check HTTP status
                if response.status != 200:
                    logger.warning(
                        f"  HTTP {response.status} for {normalized}"
                    )
                    page.close()

                    if response.status == 429:
                        # Rate limited — wait longer
                        wait_time = 60 * attempt
                        logger.warning(
                            f"  Rate limited. Waiting {wait_time}s..."
                        )
                        time.sleep(wait_time)
                        continue
                    elif response.status == 404:
                        logger.error(f"  Page not found: {normalized}")
                        return None
                    else:
                        # Other error — retry
                        time.sleep(2 * attempt)
                        continue

                # Dismiss cookie consent if present
                self._dismiss_cookie_consent(page)

                # Wait for content to render (JS-dependent content)
                page.wait_for_timeout(2000)

                # Get the full HTML
                html = page.content()

                page.close()

                if not html or len(html) < 1000:
                    logger.warning(f"  Received minimal HTML for {normalized}")
                    return None

                return {
                    "url": normalized,
                    "html": html,
                    "scraped_date": date.today(),
                    "http_status": response.status,
                }

            except Exception as e:
                logger.warning(f"  Attempt {attempt} failed: {e}")

                if attempt < settings.scraping_max_retries:
                    wait_time = 2**attempt  # Exponential backoff: 2, 4, 8 seconds
                    logger.info(f"  Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"  All {settings.scraping_max_retries} attempts failed for {normalized}"
                    )
                    return None

        return None

    def _dismiss_cookie_consent(self, page: Page):
        """
        Attempt to dismiss cookie consent banners.

        This is Groww-specific — selectors may need updates.
        """
        try:
            # Common cookie consent button selectors
            selectors = [
                "button:has-text('Accept')",
                "button:has-text('Accept All')",
                "button:has-text('I Agree')",
                "[data-testid='accept-cookies']",
                ".cookie-accept",
                "#accept-cookies",
            ]

            for selector in selectors:
                try:
                    button = page.query_selector(selector)
                    if button and button.is_visible():
                        button.click()
                        page.wait_for_timeout(1000)
                        logger.info("  Cookie consent dismissed")
                        return
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"  Cookie consent handling failed (non-critical): {e}")
