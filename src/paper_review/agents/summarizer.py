"""Summarizer Agent for creating paper summaries using LLM."""

from typing import Any, Dict, List

from loguru import logger

from paper_review.agents.base import BaseAgent
from paper_review.models import Paper, PaperSummary
from paper_review.utils import OllamaClient


class SummarizerAgent(BaseAgent):
    """Agent responsible for summarizing papers using LLM."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SummarizerAgent.

        Args:
            config: Full configuration dictionary
        """
        super().__init__(config)

        # Get summary mode config
        mode_config = config.get("summary_mode", {})
        self.mode = mode_config.get("mode", "abstract_only")  # abstract_only only for now

        # Initialize Ollama client
        ollama_base_url = mode_config.get("ollama_base_url", "http://localhost:11434")
        ollama_model = mode_config.get("ollama_model", "qwen3:8b")
        self.temperature = mode_config.get("temperature", 0.7)
        self.max_tokens = mode_config.get("max_tokens", 2000)

        self.llm = OllamaClient(base_url=ollama_base_url, model=ollama_model)

        # Get summary config
        summary_config = config.get("summary", {})
        self.language = summary_config.get("language", "ko")

        logger.info(f"Initialized SummarizerAgent (mode: {self.mode}, language: {self.language})")

    def create_summary_prompt(self, paper: Paper) -> str:
        """
        Create a prompt for summarizing a paper.

        Args:
            paper: Paper to summarize

        Returns:
            Formatted prompt string
        """
        title = paper.metadata.title
        authors = ", ".join(paper.metadata.authors[:3])  # First 3 authors
        abstract = paper.metadata.summary

        # Create prompt based on language
        if self.language == "ko":
            prompt = f"""다음 논문을 분석하고 구조화된 요약을 한국어로 작성해주세요.

논문 제목: {title}
저자: {authors}
초록: {abstract}

다음 형식으로 요약해주세요:

1. 📋 한눈에 보기 (2-3문장으로 핵심 내용 요약)

2. 🎯 연구 목적 (이 연구가 해결하고자 하는 문제)

3. 🔬 방법론 (사용된 핵심 기술이나 접근 방법)

4. 📊 주요 결과 (핵심 발견이나 성능 개선)

5. 💡 의의 및 영향 (이 연구의 학문적/실용적 가치)

각 섹션을 명확하게 구분하고, 전문 용어는 한국어로 번역하되 필요시 영문을 괄호 안에 병기해주세요.
"""
        else:
            prompt = f"""Please analyze the following paper and create a structured summary.

Paper Title: {title}
Authors: {authors}
Abstract: {abstract}

Please summarize in the following format:

1. 📋 Key Highlights (2-3 sentence core summary)

2. 🎯 Research Objective (Problem this research aims to solve)

3. 🔬 Methodology (Core techniques or approaches used)

4. 📊 Main Results (Key findings or performance improvements)

5. 💡 Significance & Impact (Academic/practical value of this research)

Please clearly separate each section.
"""

        return prompt

    def summarize_paper(self, paper: Paper) -> PaperSummary:
        """
        Create a summary for a single paper.

        Args:
            paper: Paper to summarize

        Returns:
            PaperSummary object
        """
        paper_id = paper.metadata.arxiv_id or paper.metadata.title[:20]
        logger.info(f"Creating summary for paper: {paper_id}")

        try:
            prompt = self.create_summary_prompt(paper)

            system_prompt = "You are an expert AI researcher who excels at summarizing academic papers in a clear and structured way."

            # Call LLM
            summary_text = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            logger.info(f"Successfully created summary for paper: {paper_id}")

            return PaperSummary(
                paper_id=paper_id,
                metadata=paper.metadata,
                summary=summary_text,
                image_paths=paper.image_paths,
            )

        except Exception as e:
            logger.error(f"Error creating summary for paper {paper_id}: {e}")

            return PaperSummary(
                paper_id=paper_id,
                metadata=paper.metadata,
                summary=f"Error creating summary: {str(e)}",
                image_paths=paper.image_paths,
            )

    def summarize_papers(self, papers: List[Paper]) -> List[PaperSummary]:
        """
        Create summaries for multiple papers.

        Args:
            papers: List of papers to summarize

        Returns:
            List of PaperSummary objects
        """
        logger.info(f"Creating summaries for {len(papers)} papers")

        summaries = []
        for paper in papers:
            summary = self.summarize_paper(paper)
            summaries.append(summary)

        logger.info(f"Completed creating {len(summaries)} summaries")

        return summaries

    def execute(self, papers: List[Paper]) -> List[PaperSummary]:
        """
        Execute the summarizer.

        Args:
            papers: List of papers to summarize

        Returns:
            List of summaries
        """
        return self.summarize_papers(papers)
