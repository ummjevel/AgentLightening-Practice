"""Main pipeline orchestrator for paper review service."""

from datetime import datetime
from typing import Any, Dict, List

from loguru import logger

from paper_review.agents import ArxivFetcher, HuggingFaceFetcher, NoveltyRanker, SummarizerAgent
from paper_review.models import FilterConfig, Paper, PaperSummary, SummaryReport


class PaperReviewPipeline:
    """Main pipeline that orchestrates all agents."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the pipeline.

        Args:
            config: Full configuration dictionary
        """
        self.config = config

        # Initialize agents
        self.arxiv_fetcher = ArxivFetcher(config)
        self.hf_fetcher = HuggingFaceFetcher(config)
        self.novelty_ranker = NoveltyRanker(config)
        self.summarizer = SummarizerAgent(config)

        logger.info("Initialized PaperReviewPipeline")

    async def run(
        self, filter_config: FilterConfig, process_pdfs: bool = True
    ) -> SummaryReport:
        """
        Run the full pipeline.

        Args:
            filter_config: Filter configuration
            process_pdfs: Whether to download PDFs and extract content

        Returns:
            SummaryReport with all summaries
        """
        logger.info(f"Starting pipeline with sources: {filter_config.sources}")

        all_papers: List[Paper] = []

        # Stage 1: Fetch papers from all sources
        if "arxiv" in filter_config.sources:
            arxiv_papers = self.arxiv_fetcher.fetch_metadata_only(filter_config)
            logger.info(f"Fetched {len(arxiv_papers)} arXiv papers")
            all_papers.extend(arxiv_papers)

        if "huggingface" in filter_config.sources:
            hf_papers = await self.hf_fetcher.fetch_daily_papers(filter_config)
            logger.info(f"Fetched {len(hf_papers)} HuggingFace papers")
            all_papers.extend(hf_papers)

        if not all_papers:
            logger.warning("No papers fetched from any source")
            return self._create_empty_report()

        logger.info(f"Total papers fetched: {len(all_papers)}")

        # Stage 2: Novelty ranking (arXiv only)
        arxiv_papers = [p for p in all_papers if p.metadata.source == "arxiv"]
        hf_papers = [p for p in all_papers if p.metadata.source == "huggingface"]

        if arxiv_papers and filter_config.novelty_enabled:
            logger.info(f"Ranking {len(arxiv_papers)} arXiv papers")
            ranked_arxiv = self.novelty_ranker.execute(arxiv_papers, filter_config)
            logger.info(f"Selected top {len(ranked_arxiv)} arXiv papers")
        else:
            ranked_arxiv = arxiv_papers

        # Combine ranked arXiv papers with all HF papers
        selected_papers = ranked_arxiv + hf_papers
        logger.info(
            f"Total selected papers: {len(selected_papers)} "
            f"(arXiv: {len(ranked_arxiv)}, HF: {len(hf_papers)})"
        )

        # Stage 3: Process PDFs (arXiv only, if requested)
        if process_pdfs and ranked_arxiv:
            logger.info(f"Processing {len(ranked_arxiv)} arXiv papers (downloading PDFs)")
            for paper in ranked_arxiv:
                self.arxiv_fetcher.process_paper(paper)

        # Stage 4: Summarize papers
        logger.info(f"Summarizing {len(selected_papers)} papers")
        summaries = self.summarizer.execute(selected_papers)

        # Stage 5: Create report
        report = SummaryReport(
            date=datetime.now().strftime("%Y-%m-%d"),
            total_papers=len(summaries),
            arxiv_count=len([s for s in summaries if s.metadata.source == "arxiv"]),
            huggingface_count=len([s for s in summaries if s.metadata.source == "huggingface"]),
            summaries=summaries,
        )

        logger.info(
            f"Pipeline completed: {report.total_papers} papers "
            f"(arXiv: {report.arxiv_count}, HF: {report.huggingface_count})"
        )

        return report

    def _create_empty_report(self) -> SummaryReport:
        """Create an empty report when no papers are found."""
        return SummaryReport(
            date=datetime.now().strftime("%Y-%m-%d"),
            total_papers=0,
            arxiv_count=0,
            huggingface_count=0,
            summaries=[],
        )
