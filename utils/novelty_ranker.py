"""Novelty ranking utility for filtering important papers."""

import logging
import time
import json
import requests
from typing import List, Dict, Any, Tuple


logger = logging.getLogger(__name__)


class NoveltyRanker:
    """Rank papers by novelty and importance based on abstracts."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize NoveltyRanker.

        Args:
            config: Configuration dictionary
        """
        self.config = config

        # Get novelty filter config
        filter_config = config.get('novelty_filter', {})
        self.enabled = filter_config.get('enabled', False)
        self.top_papers_count = filter_config.get('top_papers_count', 10)
        self.criteria = filter_config.get('ranking_criteria', ['novelty', 'impact', 'clarity'])

        # Ollama settings
        self.ollama_base_url = filter_config.get('ollama_base_url', 'http://localhost:11434')
        self.model = filter_config.get('ollama_model', 'qwen2.5:latest')
        self.temperature = filter_config.get('temperature', 0.3)
        logger.info(f"Initialized NoveltyRanker with Ollama (model: {self.model})")

        logger.info(f"NoveltyRanker enabled: {self.enabled}, top papers: {self.top_papers_count}")

    def rank_papers(self, papers_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank papers by novelty and importance.

        Args:
            papers_data: List of paper data dictionaries

        Returns:
            Sorted list of top N papers with ranking scores
        """
        if not self.enabled:
            logger.info("Novelty filtering disabled, returning all papers")
            return papers_data

        if len(papers_data) <= self.top_papers_count:
            logger.info(f"Only {len(papers_data)} papers, no filtering needed")
            return papers_data

        logger.info(f"Ranking {len(papers_data)} papers to select top {self.top_papers_count}")

        # Score each paper
        scored_papers = []
        for paper_data in papers_data:
            try:
                score_data = self._score_paper(paper_data)
                scored_papers.append({
                    **paper_data,
                    'novelty_score': score_data
                })
            except Exception as e:
                logger.error(f"Error scoring paper {paper_data['metadata']['arxiv_id']}: {e}")
                # Give neutral score if scoring fails
                scored_papers.append({
                    **paper_data,
                    'novelty_score': {
                        'total_score': 5.0,
                        'novelty': 5.0,
                        'impact': 5.0,
                        'clarity': 5.0,
                        'reasoning': 'Scoring failed'
                    }
                })

        # Sort by total score (descending)
        sorted_papers = sorted(
            scored_papers,
            key=lambda x: x['novelty_score']['total_score'],
            reverse=True
        )

        # Select top N
        top_papers = sorted_papers[:self.top_papers_count]

        logger.info(f"Selected top {len(top_papers)} papers")
        for i, paper in enumerate(top_papers[:5]):  # Log top 5
            metadata = paper['metadata']
            score = paper['novelty_score']['total_score']
            logger.info(f"  #{i+1}: {metadata['title'][:60]}... (score: {score:.1f})")

        return top_papers

    def _score_paper(self, paper_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Score a single paper based on novelty, impact, and clarity.

        Args:
            paper_data: Paper data dictionary

        Returns:
            Dictionary with scores for each criterion
        """
        metadata = paper_data['metadata']
        title = metadata['title']
        abstract = metadata['summary']

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
            # Use Ollama API
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"You are an expert researcher who evaluates academic papers. Always respond in valid JSON format.\n\n{prompt}",
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": 500
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            result_text = response.json()['response']

            # Parse JSON response
            # Try to extract JSON from markdown code blocks if present
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()

            scores = json.loads(result_text)

            # Calculate total score (average)
            total_score = (
                scores.get('novelty', 5.0) +
                scores.get('impact', 5.0) +
                scores.get('clarity', 5.0)
            ) / 3.0

            return {
                'total_score': total_score,
                'novelty': scores.get('novelty', 5.0),
                'impact': scores.get('impact', 5.0),
                'clarity': scores.get('clarity', 5.0),
                'reasoning': scores.get('reasoning', '')
            }

        except Exception as e:
            logger.error(f"Error scoring paper: {e}")
            # Return neutral scores on error
            return {
                'total_score': 5.0,
                'novelty': 5.0,
                'impact': 5.0,
                'clarity': 5.0,
                'reasoning': f'Error: {str(e)}'
            }
