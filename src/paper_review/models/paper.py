"""Paper data models."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class PaperMetadata(BaseModel):
    """논문 메타데이터."""

    title: str = Field(description="논문 제목")
    authors: List[str] = Field(description="저자 목록")
    summary: str = Field(description="논문 초록")
    published: datetime = Field(description="발행 날짜")
    updated: Optional[datetime] = Field(default=None, description="최종 업데이트 날짜")

    # arXiv specific fields
    arxiv_id: Optional[str] = Field(default=None, description="arXiv ID (예: 2511.14899)")
    primary_category: str = Field(description="주 카테고리")
    categories: List[str] = Field(default_factory=list, description="모든 카테고리")
    pdf_url: Optional[str] = Field(default=None, description="PDF URL")
    doi: Optional[str] = Field(default=None, description="DOI")
    journal_ref: Optional[str] = Field(default=None, description="저널 레퍼런스")
    comment: Optional[str] = Field(default=None, description="저자 코멘트")

    # HuggingFace specific fields
    upvotes: int = Field(default=0, description="Upvote 수")
    num_comments: int = Field(default=0, description="댓글 수")
    github_repo: Optional[str] = Field(default=None, description="GitHub 저장소 URL")
    github_stars: int = Field(default=0, description="GitHub 스타 수")
    project_page: Optional[str] = Field(default=None, description="프로젝트 페이지 URL")
    thumbnail: Optional[str] = Field(default=None, description="썸네일 이미지 URL")

    # Common fields
    source: Literal["arxiv", "huggingface"] = Field(description="논문 소스")
    tags: List[str] = Field(
        default_factory=list,
        description="태그 (arXiv: categories, HF: ai_keywords)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Example Paper Title",
                "authors": ["Author 1", "Author 2"],
                "summary": "This is an abstract...",
                "published": "2025-11-25T10:00:00Z",
                "arxiv_id": "2511.14899",
                "primary_category": "cs.CV",
                "categories": ["cs.CV", "cs.AI"],
                "source": "arxiv",
                "tags": ["cs.CV", "cs.AI"],
            }
        }


class NoveltyScore(BaseModel):
    """Novelty ranking 점수."""

    total_score: float = Field(description="총점 (1-10)")
    novelty: float = Field(description="참신성 점수 (1-10)")
    impact: float = Field(description="영향력 점수 (1-10)")
    clarity: float = Field(description="명확성 점수 (1-10)")
    reasoning: str = Field(description="평가 근거")


class Paper(BaseModel):
    """전체 논문 데이터."""

    metadata: PaperMetadata = Field(description="논문 메타데이터")
    pdf_path: Optional[str] = Field(default=None, description="로컬 PDF 파일 경로")
    full_text: Optional[str] = Field(default=None, description="추출된 전체 텍스트")
    image_paths: List[str] = Field(default_factory=list, description="추출된 이미지 경로")
    novelty_score: Optional[NoveltyScore] = Field(
        default=None, description="Novelty ranking 점수 (arXiv만)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "title": "Example Paper",
                    "authors": ["Author 1"],
                    "summary": "Abstract...",
                    "published": "2025-11-25T10:00:00Z",
                    "primary_category": "cs.CV",
                    "source": "arxiv",
                },
                "pdf_path": "/data/papers/2511.14899.pdf",
                "image_paths": ["/data/images/2511.14899_1.png"],
            }
        }
