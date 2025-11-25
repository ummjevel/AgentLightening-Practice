"""Summary data models."""

from typing import List

from pydantic import BaseModel, Field

from .paper import PaperMetadata


class PaperSummary(BaseModel):
    """논문 요약 데이터."""

    paper_id: str = Field(description="논문 ID (arxiv_id 또는 HF paper.id)")
    metadata: PaperMetadata = Field(description="논문 메타데이터")
    summary: str = Field(description="생성된 요약 (한국어 또는 영어)")
    image_paths: List[str] = Field(default_factory=list, description="관련 이미지 경로")

    class Config:
        json_schema_extra = {
            "example": {
                "paper_id": "2511.14899",
                "metadata": {
                    "title": "Example Paper",
                    "authors": ["Author 1"],
                    "summary": "Abstract...",
                    "published": "2025-11-25T10:00:00Z",
                    "primary_category": "cs.CV",
                    "source": "arxiv",
                },
                "summary": "## 📋 한눈에 보기\n...",
                "image_paths": ["/data/images/2511.14899_1.png"],
            }
        }


class SummaryReport(BaseModel):
    """전체 요약 리포트."""

    date: str = Field(description="리포트 생성 날짜")
    total_papers: int = Field(description="전체 논문 수")
    arxiv_count: int = Field(default=0, description="arXiv 논문 수")
    huggingface_count: int = Field(default=0, description="HuggingFace 논문 수")
    summaries: List[PaperSummary] = Field(description="논문 요약 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-11-25",
                "total_papers": 15,
                "arxiv_count": 10,
                "huggingface_count": 5,
                "summaries": [],
            }
        }
