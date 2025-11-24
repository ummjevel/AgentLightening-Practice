"""Ollama multimodal integration for PDF analysis."""

import logging
import base64
from typing import List, Dict, Any
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io
import requests


logger = logging.getLogger(__name__)


class OllamaMultimodal:
    """Ollama multimodal model integration for analyzing PDFs with images."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OllamaMultimodal.

        Args:
            config: Configuration dictionary
        """
        self.config = config

        # Get Ollama config
        ollama_config = config.get('ollama', {})
        self.enabled = ollama_config.get('enabled', False)
        self.base_url = ollama_config.get('base_url', 'http://localhost:11434')
        self.model = ollama_config.get('model', 'llava')
        self.temperature = ollama_config.get('temperature', 0.7)
        self.num_ctx = ollama_config.get('num_ctx', 4096)

        # PDF to image settings
        pdf_img_config = ollama_config.get('pdf_to_image', {})
        self.dpi = pdf_img_config.get('dpi', 150)
        self.max_pages = pdf_img_config.get('max_pages', 10)
        self.img_format = pdf_img_config.get('format', 'png')

        # Get summary config
        summary_config = config.get('summary', {})
        self.language = summary_config.get('language', 'ko')

        logger.info(f"Initialized OllamaMultimodal (enabled: {self.enabled}, model: {self.model})")

    def pdf_to_images(self, pdf_path: str) -> List[str]:
        """
        Convert PDF pages to base64 encoded images.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of base64 encoded image strings
        """
        logger.info(f"Converting PDF to images: {pdf_path}")

        images = []

        try:
            doc = fitz.open(pdf_path)
            num_pages = min(len(doc), self.max_pages)

            for page_num in range(num_pages):
                page = doc[page_num]

                # Render page to image
                mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)  # 72 is default DPI
                pix = page.get_pixmap(matrix=mat)

                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                # Convert to base64
                buffered = io.BytesIO()
                img.save(buffered, format=self.img_format.upper())
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                images.append(img_base64)

                logger.debug(f"Converted page {page_num + 1}/{num_pages}")

            doc.close()

            logger.info(f"Converted {len(images)} pages to images")

            return images

        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []

    def analyze_paper_multimodal(self, paper_data: Dict[str, Any]) -> str:
        """
        Analyze paper using multimodal model with PDF images.

        Args:
            paper_data: Paper data dictionary

        Returns:
            Generated summary text
        """
        if not self.enabled:
            raise RuntimeError("Ollama multimodal is not enabled in config")

        metadata = paper_data['metadata']
        title = metadata['title']
        authors = ', '.join(metadata['authors'][:3])
        abstract = metadata['summary']
        pdf_path = paper_data.get('pdf_path', '')

        logger.info(f"Analyzing paper with multimodal model: {title[:50]}...")

        # Convert PDF to images
        page_images = self.pdf_to_images(pdf_path)

        if not page_images:
            logger.warning("No images extracted, falling back to abstract only")
            # Fallback to abstract-only analysis
            return self._analyze_abstract_only(title, authors, abstract)

        # Create multimodal prompt
        if self.language == 'ko':
            prompt = f"""다음 논문을 분석하고 구조화된 요약을 한국어로 작성해주세요.

논문 제목: {title}
저자: {authors}
초록: {abstract}

PDF 이미지를 보고 다음을 분석해주세요:

1. 📋 한눈에 보기 (2-3문장으로 핵심 내용 요약)

2. 🎯 연구 목적 (이 연구가 해결하고자 하는 문제)

3. 🔬 방법론 (사용된 핵심 기술이나 접근 방법, 그림과 수식 참고)

4. 📊 주요 결과 (핵심 발견이나 성능 개선, 그래프나 표 참고)

5. 💡 의의 및 영향 (이 연구의 학문적/실용적 가치)

6. 🖼️ 주요 그림 설명 (논문에서 가장 중요한 그림들에 대한 설명)

각 섹션을 명확하게 구분하고, PDF 이미지에 나온 수식, 그래프, 다이어그램을 참고하여 상세히 설명해주세요."""
        else:
            prompt = f"""Please analyze the following paper and create a structured summary.

Paper Title: {title}
Authors: {authors}
Abstract: {abstract}

Analyze the PDF images and provide:

1. 📋 Key Highlights (2-3 sentence core summary)

2. 🎯 Research Objective (Problem this research aims to solve)

3. 🔬 Methodology (Core techniques or approaches, reference figures and equations)

4. 📊 Main Results (Key findings or performance improvements, reference graphs/tables)

5. 💡 Significance & Impact (Academic/practical value)

6. 🖼️ Key Figures Description (Explain the most important figures in the paper)

Provide detailed explanations referencing equations, graphs, and diagrams from the PDF images."""

        try:
            # Call Ollama API with multimodal input
            summary = self._call_ollama_multimodal(prompt, page_images)

            logger.info(f"Successfully analyzed paper with multimodal model")

            return summary

        except Exception as e:
            logger.error(f"Error in multimodal analysis: {e}")
            # Fallback to abstract only
            return self._analyze_abstract_only(title, authors, abstract)

    def _call_ollama_multimodal(self, prompt: str, images: List[str]) -> str:
        """
        Call Ollama API with multimodal input.

        Args:
            prompt: Text prompt
            images: List of base64 encoded images

        Returns:
            Generated text response
        """
        url = f"{self.base_url}/api/generate"

        # Prepare request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": images,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx
            }
        }

        logger.debug(f"Calling Ollama API: {url}")

        response = requests.post(url, json=payload, timeout=300)  # 5 min timeout

        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        return result.get('response', '')

    def _analyze_abstract_only(self, title: str, authors: str, abstract: str) -> str:
        """
        Fallback method to analyze only abstract without images.

        Args:
            title: Paper title
            authors: Paper authors
            abstract: Paper abstract

        Returns:
            Generated summary
        """
        logger.warning("Using abstract-only fallback")

        if self.language == 'ko':
            return f"""📋 한눈에 보기
이 논문은 제한된 정보로 인해 상세 분석이 불가능합니다.

논문 제목: {title}
저자: {authors}

초록 요약:
{abstract[:500]}...

⚠️ 참고: PDF 이미지 분석 실패로 초록만 표시됩니다."""
        else:
            return f"""📋 Key Highlights
Detailed analysis unavailable due to limited information.

Paper Title: {title}
Authors: {authors}

Abstract Summary:
{abstract[:500]}...

⚠️ Note: Showing abstract only due to PDF image analysis failure."""
