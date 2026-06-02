"""
Phase 1 Ingestion Pipeline.

Orchestrates the complete data ingestion workflow:
1. Scrape Groww scheme pages
2. Parse HTML to clean text
3. Tag with metadata
4. Validate and save to JSON/Parquet
"""

import json
import logging
import uuid
from datetime import date
from pathlib import Path
from typing import Optional

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, settings
from app.ingestion.scraper import GrowwScraper
from app.ingestion.parser import html_to_text, validate_content_length
from app.ingestion.metadata_tagger import tag_document, validate_metadata
from app.models.document import IngestedDocument
from app.guardrails.domain_allowlist import normalize_url

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Orchestrates Phase 1: Corpus Collection & Data Ingestion.

    Workflow:
        Scrape → Parse → Tag → Validate → Save
    """

    def __init__(self):
        self.documents: list[IngestedDocument] = []
        self.errors: list[dict] = []

    def run(self) -> list[IngestedDocument]:
        """
        Execute the full ingestion pipeline.

        Returns:
            List of successfully ingested documents.
        """
        logger.info("=" * 60)
        logger.info("PHASE 1: Corpus Collection & Data Ingestion")
        logger.info("=" * 60)

        # Step 1: Scrape
        logger.info("\n[Step 1] Scraping Groww scheme pages...")
        scraped_data = self._scrape()

        if not scraped_data:
            logger.error("No data scraped. Aborting pipeline.")
            return []

        # Step 2: Parse
        logger.info(f"\n[Step 2] Parsing {len(scraped_data)} documents...")
        parsed_data = self._parse(scraped_data)

        # Step 3: Tag & Validate
        logger.info(f"\n[Step 3] Tagging and validating documents...")
        self.documents = self._tag_and_validate(parsed_data)

        # Step 4: Save
        logger.info(f"\n[Step 4] Saving {len(self.documents)} documents...")
        self._save()

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 1 COMPLETE")
        logger.info(f"  Documents ingested: {len(self.documents)}")
        logger.info(f"  Errors: {len(self.errors)}")
        logger.info(f"  Raw data: {RAW_DATA_DIR}")
        logger.info(f"  Processed data: {PROCESSED_DATA_DIR}")
        logger.info("=" * 60)

        return self.documents

    def _scrape(self) -> list[dict]:
        """
        Step 1: Scrape all Groww scheme pages.

        Returns:
            List of raw scraped data dictionaries.
        """
        with GrowwScraper() as scraper:
            scraped = scraper.scrape_all_schemes()

        if not scraped:
            logger.error("All scraping attempts failed")
            return []

        logger.info(f"✓ Scraped {len(scraped)} pages successfully")
        return scraped

    def _parse(self, scraped_data: list[dict]) -> list[dict]:
        """
        Step 2: Parse HTML to clean text.

        Args:
            scraped_data: List of scraped data dictionaries.

        Returns:
            List of parsed data with clean text.
        """
        parsed = []

        for item in scraped_data:
            url = item["url"]
            html = item["html"]

            # Convert HTML to clean text
            clean_text = html_to_text(html)

            # Validate minimum content length
            if not validate_content_length(clean_text, settings.min_content_length):
                error_msg = (
                    f"Content too short ({len(clean_text)} chars < "
                    f"{settings.min_content_length} minimum): {url}"
                )
                logger.warning(f"✗ {error_msg}")
                self.errors.append({
                    "url": url,
                    "error": error_msg,
                    "stage": "parse",
                })
                continue

            parsed.append({
                "url": url,
                "html": html,
                "clean_text": clean_text,
                "scraped_date": item["scraped_date"],
            })

            logger.info(
                f"✓ Parsed: {url} ({len(clean_text)} chars)"
            )

        logger.info(f"✓ Parsed {len(parsed)}/{len(scraped_data)} documents")
        return parsed

    def _tag_and_validate(self, parsed_data: list[dict]) -> list[IngestedDocument]:
        """
        Step 3: Tag documents with metadata and validate.

        Args:
            parsed_data: List of parsed data dictionaries.

        Returns:
            List of validated IngestedDocument objects.
        """
        documents = []

        for item in parsed_data:
            url = item["url"]
            clean_text = item["clean_text"]
            html = item["html"]
            scraped_date = item["scraped_date"]

            # Generate unique document ID
            doc_id = str(uuid.uuid4())

            # Tag with metadata
            metadata = tag_document(url, scraped_date)

            # Validate metadata
            if not validate_metadata(metadata):
                error_msg = f"Invalid metadata for {url}: {metadata}"
                logger.warning(f"✗ {error_msg}")
                self.errors.append({
                    "url": url,
                    "error": error_msg,
                    "stage": "tag",
                })
                continue

            # Create document model
            doc = IngestedDocument(
                doc_id=doc_id,
                scheme_name=metadata["scheme_name"],
                amc_name=metadata["amc_name"],
                source_url=metadata["source_url"],
                category=metadata["category"],
                content_raw=html,
                content_clean=clean_text,
                scraped_date=scraped_date,
                last_verified_date=None,  # Could be extracted from Groww page
                is_official=True,
                domain_verified=True,
                source_type="groww_scheme_page",
            )

            documents.append(doc)

            logger.info(
                f"✓ Tagged: {doc.scheme_name} ({doc.category})"
            )

        logger.info(f"✓ Validated {len(documents)}/{len(parsed_data)} documents")
        return documents

    def _save(self):
        """
        Step 4: Save documents to JSON and Parquet files.
        """
        if not self.documents:
            logger.warning("No documents to save")
            return

        # Save as JSON (to processed dir - corpus_documents.json)
        json_path = PROCESSED_DATA_DIR / "corpus_documents.json"
        documents_json = [doc.model_dump(mode="json") for doc in self.documents]

        # Remove content_raw from JSON (too large, kept in raw data files)
        for doc_dict in documents_json:
            doc_dict["content_raw"] = "[omitted - see raw HTML files]"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(documents_json, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Saved JSON: {json_path}")

        # Also save to raw dir for Phase 1.2 compatibility (ingested_documents.json)
        raw_json_path = RAW_DATA_DIR / "ingested_documents.json"
        with open(raw_json_path, "w", encoding="utf-8") as f:
            json.dump(documents_json, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Saved JSON: {raw_json_path}")

        # Save raw HTML files for each document
        raw_html_dir = RAW_DATA_DIR / "html"
        raw_html_dir.mkdir(exist_ok=True)

        for doc in self.documents:
            filename = f"{doc.scheme_name.replace(' ', '_').lower()}.html"
            html_path = raw_html_dir / filename

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(doc.content_raw)

            logger.info(f"  Raw HTML: {html_path}")

        # Save error report
        if self.errors:
            error_path = PROCESSED_DATA_DIR / "ingestion_errors.json"
            with open(error_path, "w", encoding="utf-8") as f:
                json.dump(self.errors, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved error report: {error_path}")

        logger.info(
            f"✓ Saved {len(self.documents)} documents to {PROCESSED_DATA_DIR}"
        )


def run_ingestion() -> list[IngestedDocument]:
    """
    Convenience function to run the Phase 1 ingestion pipeline.

    Can be called directly: `python -m app.ingestion.pipeline`

    Returns:
        List of successfully ingested documents.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    pipeline = IngestionPipeline()
    return pipeline.run()


if __name__ == "__main__":
    documents = run_ingestion()

    if documents:
        print(f"\n✓ Successfully ingested {len(documents)} documents:")
        for doc in documents:
            print(f"  - {doc.scheme_name} ({doc.category})")
    else:
        print("\n✗ No documents were ingested. Check logs for errors.")
