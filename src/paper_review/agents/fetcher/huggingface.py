"""HuggingFace Daily Papers fetcher agent."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

import httpx
from loguru import logger

from paper_review.agents.base import BaseAgent
from paper_review.models import FilterConfig, Paper, PaperMetadata


class HuggingFaceFetcher(BaseAgent):
    """HuggingFace Daily Papers 수집 에이전트."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize HuggingFace fetcher.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.api_url = "https://huggingface.co/api/daily_papers"
        self.timeout = 30.0

    async def fetch_daily_papers(self, filter_config: FilterConfig) -> List[Paper]:
        """
        HuggingFace Daily Papers 수집.

        Args:
            filter_config: 필터링 설정

        Returns:
            List[Paper]: 필터링된 논문 목록
        """
        if "huggingface" not in filter_config.sources:
            self.logger.info("HuggingFace source not selected in filter")
            return []

        self.logger.info(f"Fetching HuggingFace daily papers (max: {filter_config.hf_max_papers})")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.api_url, params={"limit": filter_config.hf_max_papers}
                )
                response.raise_for_status()
                papers_data = response.json()

            self.logger.info(f"Retrieved {len(papers_data)} papers from HuggingFace API")

            papers = []
            for paper_data in papers_data:
                paper = self._parse_paper(paper_data)
                if paper and self._apply_filters(paper, filter_config):
                    papers.append(paper)

            self.logger.info(
                f"After filtering: {len(papers)} papers " f"(keywords: {filter_config.hf_keywords})"
            )

            return papers[:filter_config.hf_max_papers]

        except httpx.HTTPError as e:
            self.logger.error(f"Failed to fetch HuggingFace papers: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return []

    def _parse_paper(self, data: Dict[str, Any]) -> Paper | None:
        """
        Parse paper data from HuggingFace API response.

        Args:
            data: Raw paper data from API

        Returns:
            Paper object or None if parsing fails
        """
        try:
            paper_info = data.get("paper", {})

            # Extract author names
            authors = []
            for author in paper_info.get("authors", []):
                name = author.get("name", "Unknown")
                authors.append(name)

            # Parse dates
            published_at = paper_info.get("publishedAt")
            published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

            # Extract keywords (tags)
            keywords = paper_info.get("ai_keywords", [])

            metadata = PaperMetadata(
                title=paper_info.get("title", ""),
                authors=authors,
                summary=paper_info.get("summary", ""),
                published=published,
                arxiv_id=paper_info.get("id"),  # HF에서도 arXiv ID가 있을 수 있음
                primary_category=keywords[0] if keywords else "unknown",
                categories=keywords,
                source="huggingface",
                tags=keywords,
                upvotes=paper_info.get("upvotes", 0),
                num_comments=data.get("numComments", 0),
                github_repo=paper_info.get("githubRepo"),
                github_stars=paper_info.get("githubStars", 0),
                project_page=paper_info.get("projectPage"),
                thumbnail=data.get("thumbnail"),
            )

            return Paper(metadata=metadata)

        except Exception as e:
            self.logger.warning(f"Failed to parse paper: {e}")
            return None

    def _apply_filters(self, paper: Paper, filter_config: FilterConfig) -> bool:
        """
        Apply filters to a paper.

        Args:
            paper: Paper to filter
            filter_config: Filter configuration

        Returns:
            bool: True if paper passes filters
        """
        # 날짜 필터
        date_from, date_to = filter_config.get_date_range()
        if not (date_from <= paper.metadata.published <= date_to):
            return False

        # Upvote 필터
        if filter_config.hf_min_upvotes > 0:
            if paper.metadata.upvotes < filter_config.hf_min_upvotes:
                return False

        # 키워드 필터
        if filter_config.hf_keywords:
            paper_keywords = set(paper.metadata.tags)
            filter_keywords = set(filter_config.hf_keywords)

            if filter_config.hf_filter_mode == "AND":
                # 모든 키워드가 포함되어야 함
                if not filter_keywords.issubset(paper_keywords):
                    return False
            else:  # OR
                # 하나라도 포함되면 OK
                if not filter_keywords.intersection(paper_keywords):
                    return False

        return True

    def execute(self, filter_config: FilterConfig) -> List[Paper]:
        """
        Execute the fetcher (sync wrapper for async method).

        Args:
            filter_config: Filter configuration

        Returns:
            List[Paper]: Filtered papers
        """
        import asyncio

        return asyncio.run(self.fetch_daily_papers(filter_config))
