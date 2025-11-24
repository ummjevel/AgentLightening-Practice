"""Summarizer Agent for creating paper summaries using LLM."""

import logging
from typing import List, Dict, Any
from openai import OpenAI


logger = logging.getLogger(__name__)


class SummarizerAgent:
    """Agent responsible for summarizing papers using LLM."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SummarizerAgent.

        Args:
            config: Full configuration dictionary
        """
        self.config = config

        # Get LLM config
        llm_config = config.get('llm', {})
        self.api_key = llm_config.get('api_key')
        self.base_url = llm_config.get('base_url')
        self.model = llm_config.get('model', 'ax4')
        self.temperature = llm_config.get('temperature', 0.7)
        self.max_tokens = llm_config.get('max_tokens', 2000)

        # Get summary config
        summary_config = config.get('summary', {})
        self.language = summary_config.get('language', 'ko')

        # Initialize OpenAI client with custom base URL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        logger.info(f"Initialized SummarizerAgent with model: {self.model}")

    def create_summary_prompt(self, paper_data: Dict[str, Any]) -> str:
        """
        Create a prompt for summarizing a paper.

        Args:
            paper_data: Paper data dictionary

        Returns:
            Formatted prompt string
        """
        metadata = paper_data['metadata']
        title = metadata['title']
        authors = ', '.join(metadata['authors'][:3])  # First 3 authors
        abstract = metadata['summary']

        # Create prompt based on language
        if self.language == 'ko':
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

    def summarize_paper(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary for a single paper.

        Args:
            paper_data: Paper data dictionary

        Returns:
            Summary data dictionary
        """
        metadata = paper_data['metadata']
        paper_id = metadata['arxiv_id']

        logger.info(f"Creating summary for paper: {paper_id}")

        try:
            # Create prompt
            prompt = self.create_summary_prompt(paper_data)

            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert AI researcher who excels at summarizing academic papers in a clear and structured way."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Extract summary
            summary_text = response.choices[0].message.content

            logger.info(f"Successfully created summary for paper: {paper_id}")

            return {
                'paper_id': paper_id,
                'metadata': metadata,
                'summary': summary_text,
                'image_paths': paper_data.get('image_paths', []),
            }

        except Exception as e:
            logger.error(f"Error creating summary for paper {paper_id}: {e}")
            return {
                'paper_id': paper_id,
                'metadata': metadata,
                'summary': f"Error creating summary: {str(e)}",
                'image_paths': paper_data.get('image_paths', []),
            }

    def summarize_papers(self, paper_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create summaries for multiple papers.

        Args:
            paper_data_list: List of paper data dictionaries

        Returns:
            List of summary data dictionaries
        """
        logger.info(f"Creating summaries for {len(paper_data_list)} papers")

        summaries = []

        for paper_data in paper_data_list:
            summary = self.summarize_paper(paper_data)
            summaries.append(summary)

        logger.info(f"Completed creating {len(summaries)} summaries")

        return summaries
