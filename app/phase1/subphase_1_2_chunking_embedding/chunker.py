"""
Phase 1.2: Chunking Engine

Splits cleaned document text into semantic chunks suitable for embedding.

Strategies:
1. Heading-based split (primary)
2. Fixed-size fallback (512 tokens, 64 overlap)
3. Table-aware chunking (preserve table rows)
"""

import logging
import re
from typing import List

import tiktoken

from config import settings

logger = logging.getLogger(__name__)

# Tokenizer for chunk size calculation
TOKENIZER = tiktoken.get_encoding("cl100k_base")  # OpenAI's tokenizer


class ChunkingEngine:
    """
    Chunks document text using multiple strategies.

    Priority:
    1. Split on headings (H1/H2/H3)
    2. Merge short chunks (< 50 tokens)
    3. Split long chunks (> 512 tokens) at sentence boundaries
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        min_chunk_tokens: int = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.min_chunk_tokens = min_chunk_tokens or settings.min_chunk_tokens

    def chunk_document(self, text: str, metadata: dict) -> List[dict]:
        """
        Chunk a document into semantic segments.

        Args:
            text: Clean document text.
            metadata: Document metadata to include in chunk metadata.

        Returns:
            List of chunk dictionaries with text and metadata.
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []

        # Step 1: Split on headings
        sections = self._split_by_headings(text)

        if not sections:
            logger.warning("No sections found, treating as single section")
            sections = [("", text)]

        # Step 2: Process each section
        chunks = []
        chunk_index = 0

        for heading, content in sections:
            # Calculate tokens
            section_text = f"{heading}\n{content}".strip() if heading else content
            token_count = self._count_tokens(section_text)

            # If section is within size limit, keep as one chunk
            if token_count <= self.chunk_size:
                if token_count >= self.min_chunk_tokens:
                    chunk = {
                        "chunk_text": section_text,
                        "chunk_index": chunk_index,
                        "token_count": token_count,
                        "metadata": {
                            **metadata,
                            "section_heading": heading if heading else "Introduction",
                        },
                    }
                    chunks.append(chunk)
                    chunk_index += 1
                else:
                    logger.debug(
                        f"Skipping short section ({token_count} tokens)"
                    )
            else:
                # Split long section into smaller chunks
                sub_chunks = self._split_long_section(section_text, heading, metadata)
                for sub_chunk in sub_chunks:
                    sub_chunk["chunk_index"] = chunk_index
                    chunks.append(sub_chunk)
                    chunk_index += 1

        # Step 3: Merge short adjacent chunks
        chunks = self._merge_short_chunks(chunks)

        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks

    def _split_by_headings(self, text: str) -> List[tuple]:
        """
        Split text on heading markers (## Heading).

        Returns:
            List of (heading, content) tuples.
        """
        # Pattern: ## Heading followed by content until next heading
        pattern = r"## (.+?)\n([\s\S]*?)(?=## |\Z)"

        matches = re.findall(pattern, text)

        if not matches:
            # Check if text starts with heading
            if text.startswith("## "):
                first_newline = text.find("\n")
                if first_newline != -1:
                    heading = text[3:first_newline].strip()
                    content = text[first_newline + 1:].strip()
                    return [(heading, content)]

            # No headings found
            return []

        sections = []
        for heading, content in matches:
            sections.append((heading.strip(), content.strip()))

        return sections

    def _split_long_section(
        self, text: str, heading: str, metadata: dict
    ) -> List[dict]:
        """
        Split a long section into smaller chunks at sentence boundaries.

        Args:
            text: Section text to split.
            heading: Section heading.
            metadata: Base metadata.

        Returns:
            List of chunk dictionaries.
        """
        chunks = []

        # Split into sentences
        sentences = self._split_sentences(text)

        current_chunk = []
        current_token_count = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            # If adding this sentence exceeds chunk size, save current chunk
            if current_token_count + sentence_tokens > self.chunk_size:
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunk = {
                        "chunk_text": chunk_text,
                        "token_count": self._count_tokens(chunk_text),
                        "metadata": {
                            **metadata,
                            "section_heading": heading if heading else "Introduction",
                        },
                    }
                    chunks.append(chunk)

                # Start new chunk with overlap
                overlap_sentences = current_chunk[-3:] if len(current_chunk) >= 3 else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_token_count = self._count_tokens(" ".join(current_chunk))
            else:
                current_chunk.append(sentence)
                current_token_count += sentence_tokens

        # Don't forget the last chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if self._count_tokens(chunk_text) >= self.min_chunk_tokens:
                chunk = {
                    "chunk_text": chunk_text,
                    "token_count": self._count_tokens(chunk_text),
                    "metadata": {
                        **metadata,
                        "section_heading": heading if heading else "Introduction",
                    },
                }
                chunks.append(chunk)

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Handles periods, exclamation marks, question marks.
        """
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _merge_short_chunks(self, chunks: List[dict]) -> List[dict]:
        """
        Merge chunks that are too short with adjacent chunks.

        Args:
            chunks: List of chunk dictionaries.

        Returns:
            List with short chunks merged.
        """
        if len(chunks) <= 1:
            return chunks

        merged = []
        skip_next = False

        for i in range(len(chunks)):
            if skip_next:
                skip_next = False
                continue

            chunk = chunks[i]

            # If chunk is too short, merge with next
            if chunk["token_count"] < self.min_chunk_tokens and i < len(chunks) - 1:
                next_chunk = chunks[i + 1]
                merged_text = f"{chunk['chunk_text']}\n{next_chunk['chunk_text']}"
                merged_chunk = {
                    "chunk_text": merged_text,
                    "token_count": self._count_tokens(merged_text),
                    "metadata": {
                        **chunk["metadata"],
                        "section_heading": f"{chunk['metadata'].get('section_heading', '')} + {next_chunk['metadata'].get('section_heading', '')}",
                    },
                }
                merged.append(merged_chunk)
                skip_next = True  # Skip next chunk since we merged it
            else:
                merged.append(chunk)

        return merged

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text using OpenAI's tokenizer.

        Args:
            text: Text to tokenize.

        Returns:
            Number of tokens.
        """
        return len(TOKENIZER.encode(text))
