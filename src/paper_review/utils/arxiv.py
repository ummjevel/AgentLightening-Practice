"""arXiv API client for fetching papers."""

import arxiv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from paper_review.models import PaperMetadata


class ArxivClient:
    """Client for interacting with arXiv API."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ArxivClient.

        Args:
            config: Configuration dictionary for arXiv settings
        """
        self.category = config.get("category", "cs.LG")
        self.categories = config.get("categories", [])  # Multiple categories
        self.max_results = config.get("max_results", 1000)
        self.sort_by = config.get("sort_by", "submittedDate")
        self.sort_order = config.get("sort_order", "descending")

        # Create arXiv client
        self.client = arxiv.Client()

        logger.info(f"Initialized ArxivClient for category: {self.category}")

    def fetch_recent_papers(
        self, categories: List[str] | None = None, max_results: int | None = None
    ) -> List[arxiv.Result]:
        """
        Fetch recent papers from arXiv.

        Args:
            categories: List of categories to search (overrides config)
            max_results: Maximum number of results (overrides config)

        Returns:
            List of arXiv paper results
        """
        cats = categories or self.categories or [self.category]
        max_res = max_results or self.max_results

        logger.info(f"Fetching {max_res} recent papers from categories: {cats}")

        try:
            # Create query for multiple categories with OR condition
            if len(cats) > 1:
                query = " OR ".join([f"cat:{cat}" for cat in cats])
            else:
                query = f"cat:{cats[0]}"

            search = arxiv.Search(
                query=query,
                max_results=max_res,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )

            # Fetch results
            results = list(self.client.results(search))

            logger.info(f"Successfully fetched {len(results)} papers")

            return results

        except Exception as e:
            logger.error(f"Error fetching papers: {e}")
            logger.info("Trying fallback search method...")

            try:
                # Fallback: search by category in all field
                query = " OR ".join(cats)
                search = arxiv.Search(
                    query=query,
                    max_results=max_res * 2,  # Get more to filter later
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending,
                )

                all_results = list(self.client.results(search))

                # Filter by category
                results = [r for r in all_results if any(cat in r.categories for cat in cats)][
                    :max_res
                ]

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
        Path(download_dir).mkdir(parents=True, exist_ok=True)

        # Generate filename from paper ID
        paper_id = paper.entry_id.split("/")[-1]
        filename = f"{paper_id}.pdf"
        filepath = Path(download_dir) / filename

        # Check if PDF already exists
        if filepath.exists():
            logger.info(f"PDF already exists, skipping download: {paper_id}")
            return str(filepath)

        # Download PDF
        logger.info(f"Downloading PDF for paper: {paper_id}")
        paper.download_pdf(dirpath=download_dir, filename=filename)

        logger.info(f"PDF downloaded to: {filepath}")

        return str(filepath)

    def to_paper_metadata(self, paper: arxiv.Result) -> PaperMetadata:
        """
        Convert arXiv result to PaperMetadata.

        Args:
            paper: arXiv paper result

        Returns:
            PaperMetadata object
        """
        return PaperMetadata(
            title=paper.title,
            authors=[author.name for author in paper.authors],
            summary=paper.summary,
            published=paper.published,
            updated=paper.updated,
            arxiv_id=paper.entry_id.split("/")[-1],
            pdf_url=paper.pdf_url,
            primary_category=paper.primary_category,
            categories=paper.categories,
            doi=paper.doi,
            journal_ref=paper.journal_ref,
            comment=paper.comment,
            source="arxiv",
            tags=paper.categories,  # For arXiv, tags = categories
        )
