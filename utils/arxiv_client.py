"""arXiv API client for fetching papers."""

import arxiv
import logging
from typing import List, Dict, Any
from datetime import datetime


logger = logging.getLogger(__name__)


class ArxivClient:
    """Client for interacting with arXiv API."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ArxivClient.

        Args:
            config: Configuration dictionary for arXiv settings
        """
        self.category = config.get('category', 'eess.AS')
        self.max_results = config.get('max_results', 10)
        self.sort_by = config.get('sort_by', 'submittedDate')
        self.sort_order = config.get('sort_order', 'descending')

        # Create arXiv client
        self.client = arxiv.Client()

        logger.info(f"Initialized ArxivClient for category: {self.category}")

    def fetch_recent_papers(self) -> List[arxiv.Result]:
        """
        Fetch recent papers from arXiv.

        Returns:
            List of arXiv paper results
        """
        logger.info(f"Fetching {self.max_results} recent papers from {self.category}")

        try:
            # Create search query with simpler approach
            # Use category filter directly
            search = arxiv.Search(
                query=f"cat:{self.category}",
                max_results=self.max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            # Fetch results
            results = list(self.client.results(search))

            logger.info(f"Successfully fetched {len(results)} papers")

            return results

        except Exception as e:
            logger.error(f"Error fetching papers: {e}")
            # Try alternative query without category filter
            logger.info("Trying alternative search method...")

            try:
                # Fallback: search by category in all field
                search = arxiv.Search(
                    query=f"{self.category}",
                    max_results=self.max_results * 2,  # Get more to filter later
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )

                all_results = list(self.client.results(search))

                # Filter by category
                results = [
                    r for r in all_results
                    if self.category in r.categories
                ][:self.max_results]

                logger.info(f"Successfully fetched {len(results)} papers using fallback method")

                return results

            except Exception as fallback_error:
                logger.error(f"Fallback method also failed: {fallback_error}")
                return []

    def download_pdf(self, paper: arxiv.Result, download_dir: str) -> str:
        """
        Download PDF for a paper (skip if already exists).

        Args:
            paper: arXiv paper result
            download_dir: Directory to save PDF

        Returns:
            Path to downloaded PDF file
        """
        import os
        os.makedirs(download_dir, exist_ok=True)

        # Generate filename from paper ID
        paper_id = paper.entry_id.split('/')[-1]
        filename = f"{paper_id}.pdf"
        filepath = os.path.join(download_dir, filename)

        # Check if PDF already exists
        if os.path.exists(filepath):
            logger.info(f"PDF already exists, skipping download: {paper_id}")
            return filepath

        # Download PDF
        logger.info(f"Downloading PDF for paper: {paper_id}")
        paper.download_pdf(dirpath=download_dir, filename=filename)

        logger.info(f"PDF downloaded to: {filepath}")

        return filepath

    def extract_metadata(self, paper: arxiv.Result) -> Dict[str, Any]:
        """
        Extract metadata from arXiv paper.

        Args:
            paper: arXiv paper result

        Returns:
            Dictionary of paper metadata
        """
        return {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'summary': paper.summary,
            'published': paper.published.strftime('%Y-%m-%d'),
            'updated': paper.updated.strftime('%Y-%m-%d') if paper.updated else None,
            'arxiv_id': paper.entry_id.split('/')[-1],
            'pdf_url': paper.pdf_url,
            'primary_category': paper.primary_category,
            'categories': paper.categories,
            'doi': paper.doi,
            'journal_ref': paper.journal_ref,
            'comment': paper.comment,
        }
