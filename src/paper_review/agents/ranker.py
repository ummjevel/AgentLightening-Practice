"""Novelty ranking agent for filtering important papers."""

import json
from typing import Any, Dict, List

from loguru import logger

from paper_review.agents.base import BaseAgent
from paper_review.models import FilterConfig, NoveltyScore, Paper
from paper_review.utils import OllamaClient


class NoveltyRanker(BaseAgent):
    """Rank papers by novelty and importance based on abstracts."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize NoveltyRanker.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)

        # Get novelty filter config
        filter_config = config.get("novelty_filter", {})
        self.enabled = filter_config.get("enabled", True)
        self.top_papers_count = filter_config.get("top_papers_count", 10)
        self.criteria = filter_config.get("ranking_criteria", ["novelty", "impact", "clarity"])

        # Initialize Ollama client
        ollama_base_url = filter_config.get("ollama_base_url", "http://localhost:11434")
        ollama_model = filter_config.get("ollama_model", "qwen3:8b")
        self.temperature = filter_config.get("temperature", 0.3)

        self.llm = OllamaClient(base_url=ollama_base_url, model=ollama_model)

        logger.info(f"Initialized NoveltyRanker (enabled: {self.enabled}, top: {self.top_papers_count})")

    def rank_papers(self, papers: List[Paper], top_n: int | None = None) -> List[Paper]:
        """
        Rank papers by novelty and importance.

        Args:
            papers: List of Paper objects
            top_n: Number of top papers to select (overrides config)

        Returns:
            Sorted list of top N papers with novelty scores
        """
        if not self.enabled:
            logger.info("Novelty filtering disabled, returning all papers")
            return papers

        n = top_n or self.top_papers_count

        if len(papers) <= n:
            logger.info(f"Only {len(papers)} papers, no filtering needed")
            return papers

        logger.info(f"Ranking {len(papers)} papers to select top {n}")

        # Score each paper
        for paper in papers:
            if paper.metadata.source == "arxiv":  # Only rank arXiv papers
                try:
                    score = self._score_paper(paper)
                    paper.novelty_score = score
                except Exception as e:
                    logger.error(f"Error scoring paper {paper.metadata.arxiv_id}: {e}")
                    # Give neutral score if scoring fails
                    paper.novelty_score = NoveltyScore(
                        total_score=5.0,
                        novelty=5.0,
                        impact=5.0,
                        clarity=5.0,
                        reasoning="Scoring failed",
                    )

        # Sort by total score (descending)
        scored_papers = [p for p in papers if p.novelty_score is not None]
        sorted_papers = sorted(
            scored_papers, key=lambda x: x.novelty_score.total_score, reverse=True
        )

        # Select top N
        top_papers = sorted_papers[:n]

        logger.info(f"Selected top {len(top_papers)} papers")
        for i, paper in enumerate(top_papers[:5]):  # Log top 5
            score = paper.novelty_score.total_score if paper.novelty_score else 0
            logger.info(f"  #{i+1}: {paper.metadata.title[:60]}... (score: {score:.1f})")

        return top_papers

    def _score_paper(self, paper: Paper) -> NoveltyScore:
        """
        Score a single paper based on novelty, impact, and clarity.

        Args:
            paper: Paper to score

        Returns:
            NoveltyScore object
        """
        title = paper.metadata.title
        abstract = paper.metadata.summary

        # Create scoring prompt
        prompt = f"""다음 논문의 초록을 분석하고 각 기준에 대해 1-10점으로 평가해주세요.

논문 제목: {title}
초록: {abstract}

평가 기준:
1. Novelty (참신성): 이 연구가 얼마나 새롭고 혁신적인가?
2. Impact (영향력): 이 연구가 해당 분야에 얼마나 큰 영향을 미칠 수 있는가?
3. Clarity (명확성): 초록이 얼마나 명확하고 잘 작성되었는가?

다음 JSON 형식으로만 답변해주세요:
{{
  "novelty": <1-10>,
  "impact": <1-10>,
  "clarity": <1-10>,
  "reasoning": "<간단한 이유 1-2문장>"
}}"""

        try:
            system_prompt = "You are an expert researcher who evaluates academic papers. Always respond in valid JSON format."
            result_text = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=self.temperature,
                max_tokens=500,
                format_json=True,
            )

            # Parse JSON response
            # Try to extract JSON from markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            scores = json.loads(result_text)

            # Calculate total score (average)
            total_score = (
                scores.get("novelty", 5.0) + scores.get("impact", 5.0) + scores.get("clarity", 5.0)
            ) / 3.0

            return NoveltyScore(
                total_score=total_score,
                novelty=scores.get("novelty", 5.0),
                impact=scores.get("impact", 5.0),
                clarity=scores.get("clarity", 5.0),
                reasoning=scores.get("reasoning", ""),
            )

        except Exception as e:
            logger.error(f"Error scoring paper: {e}")
            # Return neutral scores on error
            return NoveltyScore(
                total_score=5.0,
                novelty=5.0,
                impact=5.0,
                clarity=5.0,
                reasoning=f"Error: {str(e)}",
            )

    def execute(self, papers: List[Paper], filter_config: FilterConfig) -> List[Paper]:
        """
        Execute the ranker.

        Args:
            papers: List of papers to rank
            filter_config: Filter configuration

        Returns:
            Ranked and filtered papers
        """
        if not filter_config.novelty_enabled:
            return papers

        return self.rank_papers(papers, top_n=filter_config.novelty_top_n)
