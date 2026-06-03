from datetime import date

from app.api.routes.chat import _extract_last_updated


def test_extract_last_updated_always_returns_today():
    """last_updated should always be today's date regardless of chunk metadata."""
    chunks = [
        {"metadata": {"scraped_date": "2026-05-28"}},
        {"metadata": {"scraped_date": "2026-05-26"}},
    ]
    assert _extract_last_updated(chunks) == date.today().strftime("%Y-%m-%d")


def test_extract_last_updated_with_empty_chunks():
    assert _extract_last_updated([]) == date.today().strftime("%Y-%m-%d")
