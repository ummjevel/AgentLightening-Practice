"""Fetcher Agent for collecting papers from arXiv."""

import logging
from typing import List, Dict, Any
from pathlib import Path

from utils.arxiv_client import ArxivClient
from utils.pdf_processor import PDFProcessor
from utils.image_extractor import ImageExtractor


logger = logging.getLogger(__name__)


class FetcherAgent:
    """Agent responsible for fetching papers and extracting content."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize FetcherAgent.

        Args:
            config: Full configuration dictionary
        """
        self.config = config

        # Initialize components
        self.arxiv_client = ArxivClient(config.get('arxiv', {}))
        self.pdf_processor = PDFProcessor(config.get('pdf', {}))
        self.image_extractor = ImageExtractor(config.get('pdf', {}))

        # Get paths from config
        paths = config.get('paths', {})
        self.papers_dir = paths.get('papers_dir', 'data/papers')
        self.images_dir = paths.get('images_dir', 'data/images')

        # Create directories
        Path(self.papers_dir).mkdir(parents=True, exist_ok=True)
        Path(self.images_dir).mkdir(parents=True, exist_ok=True)

        logger.info("Initialized FetcherAgent")

    def fetch_papers(self) -> List[Dict[str, Any]]:
        """
        Fetch recent papers from arXiv.

        Returns:
            List of paper data dictionaries
        """
        logger.info("Starting paper fetching process")

        # Fetch papers from arXiv
        papers = self.arxiv_client.fetch_recent_papers()

        paper_data_list = []

        for paper in papers:
            try:
                # Extract metadata
                metadata = self.arxiv_client.extract_metadata(paper)
                paper_id = metadata['arxiv_id']

                logger.info(f"Processing paper: {paper_id} - {metadata['title'][:50]}...")

                # Download PDF
                pdf_path = self.arxiv_client.download_pdf(paper, self.papers_dir)

                # Extract text
                full_text = self.pdf_processor.extract_text(pdf_path)

                # Extract images
                image_paths = self.image_extractor.extract_images(
                    pdf_path,
                    self.images_dir,
                    paper_id
                )

                # Combine all data
                paper_data = {
                    'metadata': metadata,
                    'pdf_path': pdf_path,
                    'full_text': full_text,
                    'image_paths': image_paths,
                }

                paper_data_list.append(paper_data)

                logger.info(f"Successfully processed paper: {paper_id}")

            except Exception as e:
                logger.error(f"Error processing paper {paper.entry_id}: {e}")
                continue

        logger.info(f"Completed fetching {len(paper_data_list)} papers")

        return paper_data_list
