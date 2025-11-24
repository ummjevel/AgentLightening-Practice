"""PDF processing utilities."""

import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any
from pathlib import Path


logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF files to extract text and metadata."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize PDFProcessor.

        Args:
            config: Configuration dictionary for PDF settings
        """
        self.config = config
        logger.info("Initialized PDFProcessor")

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        logger.info(f"Extracting text from: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)
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

    def extract_text_by_sections(self, pdf_path: str) -> Dict[str, str]:
        """
        Extract text organized by common paper sections.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with section names as keys and text as values
        """
        full_text = self.extract_text(pdf_path)

        # Common section headers in papers
        section_keywords = {
            'abstract': ['abstract', 'summary'],
            'introduction': ['introduction', '1. introduction'],
            'methodology': ['method', 'methodology', 'approach', 'model'],
            'results': ['results', 'experiments', 'evaluation'],
            'conclusion': ['conclusion', 'discussion', 'future work'],
        }

        sections = {
            'full_text': full_text,
            'abstract': '',
            'introduction': '',
            'methodology': '',
            'results': '',
            'conclusion': '',
        }

        # Simple section extraction (can be improved with better parsing)
        lines = full_text.lower().split('\n')
        current_section = None

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Check if line is a section header
            for section, keywords in section_keywords.items():
                if any(keyword in line_stripped for keyword in keywords):
                    current_section = section
                    break

        return sections

    def get_page_count(self, pdf_path: str) -> int:
        """
        Get number of pages in PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Number of pages
        """
        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception as e:
            logger.error(f"Error getting page count: {e}")
            return 0

    def get_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary of PDF metadata
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            page_count = len(doc)
            doc.close()

            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'page_count': page_count,
            }
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
