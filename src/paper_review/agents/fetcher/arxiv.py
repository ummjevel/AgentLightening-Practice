"""arXiv papers fetcher agent."""

from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from paper_review.agents.base import BaseAgent
from paper_review.models import FilterConfig, Paper
from paper_review.utils import ArxivClient, ImageExtractor, PDFProcessor


class ArxivFetcher(BaseAgent):
    """Agent responsible for fetching papers from arXiv."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ArxivFetcher.

        Args:
            config: Full configuration dictionary
        """
        super().__init__(config)

        # Initialize components
        self.arxiv_client = ArxivClient(config.get("arxiv", {}))
        self.pdf_processor = PDFProcessor(config.get("pdf", {}))
        self.image_extractor = ImageExtractor(config.get("pdf", {}))

        # Get paths from config
        paths = config.get("paths", {})
        self.papers_dir = Path(paths.get("papers_dir", "data/papers"))
        self.images_dir = Path(paths.get("images_dir", "data/images"))

        # Create directories
        self.papers_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Initialized ArxivFetcher")

    def fetch_metadata_only(self, filter_config: FilterConfig) -> List[Paper]:
        """
        Fetch only metadata from arXiv (no PDF download).

        This is the first stage of the 2-stage pipeline.

        Args:
            filter_config: Filter configuration

        Returns:
            List of papers with metadata only
        """
        if "arxiv" not in filter_config.sources:
            logger.info("arXiv source not selected in filter")
            return []

        logger.info("Fetching arXiv papers metadata only")

        # Fetch papers from arXiv
        arxiv_results = self.arxiv_client.fetch_recent_papers(
            categories=filter_config.arxiv_categories if filter_config.arxiv_categories else None
        )

        papers = []
        for arxiv_result in arxiv_results:
            metadata = self.arxiv_client.to_paper_metadata(arxiv_result)
            paper = Paper(metadata=metadata)

            # Apply filters
            if self._apply_filters(paper, filter_config):
                papers.append(paper)

        logger.info(
            f"Fetched {len(papers)} papers from arXiv "
            f"(categories: {filter_config.arxiv_categories or ['all']})"
        )

        return papers

    def process_paper(self, paper: Paper) -> Paper:
        """
        Download PDF and extract content from a single paper.

        This is the second stage of the 2-stage pipeline.

        Args:
            paper: Paper with metadata

        Returns:
            Paper with PDF, text, and images
        """
        paper_id = paper.metadata.arxiv_id
        if not paper_id:
            logger.warning("Paper has no arXiv ID, skipping processing")
            return paper

        try:
            logger.info(f"Processing paper: {paper_id}")

            # Download PDF (skip if exists)
            pdf_url = paper.metadata.pdf_url
            if pdf_url:
                # Create a temporary arxiv.Result-like object for download
                import arxiv

                # Fetch the paper again to get the Result object for download
                search = arxiv.Search(id_list=[paper_id])
                arxiv_results = list(search.results())

                if arxiv_results:
                    arxiv_result = arxiv_results[0]
                    pdf_path = self.arxiv_client.download_pdf(arxiv_result, str(self.papers_dir))
                    paper.pdf_path = pdf_path

                    # Extract text
                    full_text = self.pdf_processor.extract_text(pdf_path)
                    paper.full_text = full_text

                    # Extract images
                    image_paths = self.image_extractor.extract_images(
                        pdf_path, str(self.images_dir), paper_id
                    )
                    paper.image_paths = image_paths

                    logger.info(f"Successfully processed paper: {paper_id}")

            return paper

        except Exception as e:
            logger.error(f"Error processing paper {paper_id}: {e}")
            return paper

    def _apply_filters(self, paper: Paper, filter_config: FilterConfig) -> bool:
        """
        Apply filters to a paper.

        Args:
            paper: Paper to filter
            filter_config: Filter configuration

        Returns:
            bool: True if paper passes filters
        """
        # Date filter
        date_from, date_to = filter_config.get_date_range()
        if not (date_from <= paper.metadata.published <= date_to):
            return False

        # Category filter (AND/OR logic)
        if filter_config.arxiv_categories:
            paper_categories = set(paper.metadata.categories)
            filter_categories = set(filter_config.arxiv_categories)

            if filter_config.arxiv_filter_mode == "AND":
                # All categories must be present
                if not filter_categories.issubset(paper_categories):
                    return False
            else:  # OR
                # At least one category must be present
                if not filter_categories.intersection(paper_categories):
                    return False

        return True

    def execute(self, filter_config: FilterConfig, process_pdfs: bool = False) -> List[Paper]:
        """
        Execute the fetcher.

        Args:
            filter_config: Filter configuration
            process_pdfs: Whether to download PDFs and extract content

        Returns:
            List of papers
        """
        # Stage 1: Fetch metadata
        papers = self.fetch_metadata_only(filter_config)

        # Stage 2: Process PDFs (optional)
        if process_pdfs and papers:
            logger.info(f"Processing {len(papers)} papers (downloading PDFs and extracting content)")
            papers = [self.process_paper(paper) for paper in papers]

        return papers
