"""Summarizer Agent for creating paper summaries using LLM."""

import logging
import requests
from typing import List, Dict, Any, Optional
from openai import OpenAI
from utils.ollama_multimodal import OllamaMultimodal


logger = logging.getLogger(__name__)


class SummarizerAgent:
    """Agent responsible for summarizing papers using LLM."""

    def __init__(self, config: Dict[str, Any], tracker: Optional[Any] = None):
        """
        Initialize SummarizerAgent.

        Args:
            config: Full configuration dictionary
            tracker: Optional Agent Lightning tracker for optimization
        """
        self.config = config
        self.tracker = tracker

        # Get summary mode
        mode_config = config.get('summary_mode', {})
        self.mode = mode_config.get('mode', 'abstract_only')  # abstract_only or multimodal

        # Check if using Ollama for abstract_only mode
        self.use_ollama = mode_config.get('use_ollama', False)

        if self.use_ollama:
            # Ollama settings for abstract summarization
            self.ollama_base_url = mode_config.get('ollama_base_url', 'http://localhost:11434')
            self.model = mode_config.get('ollama_model', 'qwen3:8b')
            self.temperature = mode_config.get('temperature', 0.7)
            self.max_tokens = mode_config.get('max_tokens', 2000)
            logger.info(f"Initialized SummarizerAgent with Ollama (model: {self.model})")
        else:
            # Get LLM config for cloud API
            llm_config = config.get('llm', {})
            self.api_key = llm_config.get('api_key')
            self.base_url = llm_config.get('base_url')
            self.model = llm_config.get('model', 'ax4')
            self.temperature = llm_config.get('temperature', 0.7)
            self.max_tokens = llm_config.get('max_tokens', 2000)

            # Initialize OpenAI client with custom base URL
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info(f"Initialized SummarizerAgent with cloud LLM (model: {self.model})")

        # Get summary config
        summary_config = config.get('summary', {})
        self.language = summary_config.get('language', 'ko')

        # Initialize Ollama multimodal if mode is multimodal
        self.ollama = None
        if self.mode == 'multimodal':
            self.ollama = OllamaMultimodal(config)
            logger.info("Multimodal mode enabled with Ollama")

        logger.info(f"SummarizerAgent mode: {self.mode}, use_ollama: {self.use_ollama}")
        if self.tracker:
            logger.info("Agent Lightning tracking enabled for SummarizerAgent")

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

        logger.info(f"Creating summary for paper: {paper_id} (mode: {self.mode})")

        try:
            event_id = ""

            # Choose summarization method based on mode
            if self.mode == 'multimodal' and self.ollama and self.ollama.enabled:
                # Use Ollama multimodal analysis
                summary_text = self.ollama.analyze_paper_multimodal(paper_data)

                # Track with Agent Lightning
                if self.tracker:
                    event_id = self.tracker.emit_prompt(
                        agent_name="SummarizerAgent_Multimodal",
                        prompt=f"Multimodal analysis of {metadata['title']}",
                        metadata={
                            'paper_id': paper_id,
                            'mode': 'multimodal',
                            'model': self.ollama.model
                        }
                    )
                    self.tracker.emit_response(
                        event_id=event_id,
                        response=summary_text,
                        metadata={'mode': 'multimodal'}
                    )

            else:
                # Use abstract-only analysis (default)
                prompt = self.create_summary_prompt(paper_data)

                # Track prompt with Agent Lightning
                if self.tracker:
                    event_id = self.tracker.emit_prompt(
                        agent_name="SummarizerAgent",
                        prompt=prompt,
                        metadata={
                            'paper_id': paper_id,
                            'title': metadata['title'],
                            'model': self.model,
                            'temperature': self.temperature,
                            'mode': 'abstract_only',
                            'use_ollama': self.use_ollama
                        }
                    )

                # Call LLM (Ollama or cloud API)
                if self.use_ollama:
                    # Use Ollama API
                    response = requests.post(
                        f"{self.ollama_base_url}/api/generate",
                        json={
                            "model": self.model,
                            "prompt": f"You are an expert AI researcher who excels at summarizing academic papers in a clear and structured way.\n\n{prompt}",
                            "stream": False,
                            "options": {
                                "temperature": self.temperature,
                                "num_predict": self.max_tokens
                            }
                        },
                        timeout=120
                    )
                    response.raise_for_status()
                    summary_text = response.json()['response']
                    tokens_used = 0  # Ollama doesn't return token count
                    finish_reason = "stop"
                else:
                    # Use cloud API
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
                    tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
                    finish_reason = response.choices[0].finish_reason

                # Track response with Agent Lightning
                if self.tracker and event_id:
                    self.tracker.emit_response(
                        event_id=event_id,
                        response=summary_text,
                        metadata={
                            'tokens_used': tokens_used,
                            'finish_reason': finish_reason
                        }
                    )

                    # Emit a reward based on summary length (simple heuristic)
                    summary_length = len(summary_text)
                    if 500 <= summary_length <= 2000:
                        reward = 0.8  # Good summary length
                    elif 200 <= summary_length < 500:
                        reward = 0.5  # Too short
                    else:
                        reward = 0.3  # Too long or too short

                    self.tracker.emit_reward(
                        event_id=event_id,
                        reward=reward,
                        reason=f"Summary length: {summary_length} characters"
                    )

            logger.info(f"Successfully created summary for paper: {paper_id}")

            return {
                'paper_id': paper_id,
                'metadata': metadata,
                'summary': summary_text,
                'image_paths': paper_data.get('image_paths', []),
            }

        except Exception as e:
            logger.error(f"Error creating summary for paper {paper_id}: {e}")

            # Track error with Agent Lightning
            if self.tracker and event_id:
                self.tracker.emit_reward(
                    event_id=event_id,
                    reward=-1.0,
                    reason=f"Error: {str(e)}"
                )

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
