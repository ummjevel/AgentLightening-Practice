"""PDF processing utilities."""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Any, Dict

from loguru import logger


class PDFProcessor:
    """Process PDF files to extract text and metadata."""

    def __init__(self, config: Dict[str, Any] | None = None):
        """
        Initialize PDFProcessor.

        Args:
            config: Configuration dictionary for PDF settings
        """
        self.config = config or {}
        logger.info("Initialized PDFProcessor")

    def extract_text(self, pdf_path: str | Path) -> str:
        """
        Extract all text from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        logger.info(f"Extracting text from: {pdf_path}")

        try:
            doc = fitz.open(str(pdf_path))
            text_parts = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                text_parts.append(text)

            doc.close()

            full_text = "\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from {len(text_parts)} pages")

            return full_text

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def get_page_count(self, pdf_path: str | Path) -> int:
        """
        Get number of pages in PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Number of pages
        """
        try:
            doc = fitz.open(str(pdf_path))
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception as e:
            logger.error(f"Error getting page count: {e}")
            return 0

    def get_metadata(self, pdf_path: str | Path) -> Dict[str, Any]:
        """
        Extract PDF metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary of PDF metadata
        """
        try:
            doc = fitz.open(str(pdf_path))
            metadata = doc.metadata
            page_count = len(doc)
            doc.close()

            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "page_count": page_count,
            }
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
