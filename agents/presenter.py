"""Presenter Agent for generating summary reports."""

import logging
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from jinja2 import Template
import base64


logger = logging.getLogger(__name__)


class PresenterAgent:
    """Agent responsible for creating visual summary reports."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize PresenterAgent.

        Args:
            config: Full configuration dictionary
        """
        self.config = config

        # Get paths from config
        paths = config.get('paths', {})
        self.summaries_dir = paths.get('summaries_dir', 'data/summaries')
        self.templates_dir = paths.get('templates_dir', 'templates')

        # Get output config
        output_config = config.get('output', {})
        self.output_format = output_config.get('format', 'html')
        self.filename_template = output_config.get('filename_template', '{date}-arxiv-summary.{format}')

        # Create directories
        Path(self.summaries_dir).mkdir(parents=True, exist_ok=True)

        logger.info("Initialized PresenterAgent")

    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image to base64 for embedding in HTML.

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded image string
        """
        try:
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')

                # Determine MIME type from extension
                ext = Path(image_path).suffix.lower()
                mime_types = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                }
                mime_type = mime_types.get(ext, 'image/png')

                return f"data:{mime_type};base64,{img_base64}"

        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return ""

    def _load_template(self) -> Template:
        """
        Load HTML template.

        Returns:
            Jinja2 Template object
        """
        template_path = Path(self.templates_dir) / "summary_report.html"

        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            # Use default template if file doesn't exist
            logger.warning(f"Template file not found at {template_path}, using default template")
            template_content = self._get_default_template()

        return Template(template_content)

    def _get_default_template(self) -> str:
        """
        Get default HTML template.

        Returns:
            Default template string
        """
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arXiv 논문 요약 - {{ date }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .paper {
            background: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .paper-title {
            color: #333;
            font-size: 1.8em;
            margin-bottom: 15px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .paper-meta {
            color: #666;
            font-size: 0.95em;
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .paper-meta strong {
            color: #444;
        }
        .summary-section {
            margin: 20px 0;
            white-space: pre-wrap;
            line-height: 1.8;
        }
        .images {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .image-container {
            text-align: center;
        }
        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .image-caption {
            margin-top: 10px;
            font-size: 0.9em;
            color: #666;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
        a {
            color: #667eea;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 arXiv 논문 일일 요약</h1>
        <p>{{ date }} | {{ category }}</p>
        <p>총 {{ papers|length }}개의 논문</p>
    </div>

    {% for paper in papers %}
    <div class="paper">
        <h2 class="paper-title">{{ loop.index }}. {{ paper.metadata.title }}</h2>

        <div class="paper-meta">
            <p><strong>저자:</strong> {{ paper.metadata.authors|join(', ') }}</p>
            <p><strong>제출일:</strong> {{ paper.metadata.published }}</p>
            <p><strong>arXiv ID:</strong> <a href="{{ paper.metadata.pdf_url }}" target="_blank">{{ paper.metadata.arxiv_id }}</a></p>
            <p><strong>카테고리:</strong> {{ paper.metadata.categories|join(', ') }}</p>
        </div>

        <div class="summary-section">
{{ paper.summary }}
        </div>

        {% if paper.images %}
        <h3>🖼️ 주요 그림</h3>
        <div class="images">
            {% for image in paper.images %}
            <div class="image-container">
                <img src="{{ image }}" alt="Figure {{ loop.index }}">
                <p class="image-caption">Figure {{ loop.index }}</p>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    {% endfor %}

    <div class="footer">
        <p>Generated by arXiv Paper Summarizer | Powered by SKT-AI A.X-4.0</p>
    </div>
</body>
</html>"""

    def create_report(self, summaries: List[Dict[str, Any]]) -> str:
        """
        Create summary report from summaries.

        Args:
            summaries: List of summary dictionaries

        Returns:
            Path to generated report file
        """
        logger.info(f"Creating summary report for {len(summaries)} papers")

        # Prepare data for template
        papers_data = []

        for summary in summaries:
            # Encode images to base64 for embedding
            encoded_images = []
            for img_path in summary.get('image_paths', []):
                encoded_img = self._encode_image_to_base64(img_path)
                if encoded_img:
                    encoded_images.append(encoded_img)

            papers_data.append({
                'metadata': summary['metadata'],
                'summary': summary['summary'],
                'images': encoded_images,
            })

        # Prepare template context
        context = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'category': self.config.get('arxiv', {}).get('category', 'eess.AS'),
            'papers': papers_data,
        }

        # Load and render template
        template = self._load_template()
        html_content = template.render(context)

        # Generate output filename
        filename = self.filename_template.format(
            date=context['date'],
            format=self.output_format
        )
        output_path = Path(self.summaries_dir) / filename

        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Summary report created: {output_path}")

        return str(output_path)
