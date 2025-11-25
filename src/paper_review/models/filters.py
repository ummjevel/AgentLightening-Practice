"""Filtering configuration models."""

from datetime import date, datetime, timedelta
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class FilterConfig(BaseModel):
    """필터링 설정 (AND/OR 선택 가능)."""

    # 소스 필터
    sources: List[Literal["arxiv", "huggingface"]] = Field(
        default=["arxiv", "huggingface"],
        description="논문 소스 (arxiv, huggingface, 또는 둘 다)",
    )

    # 날짜 필터
    date_from: Optional[date] = Field(
        default=None, description="시작 날짜 (None이면 days_back 사용)"
    )
    date_to: Optional[date] = Field(default=None, description="종료 날짜 (None이면 오늘)")
    days_back: int = Field(default=1, ge=1, description="최근 N일 (date_from이 None일 때 사용)")

    # arXiv 필터
    arxiv_categories: List[str] = Field(
        default_factory=list, description="arXiv 카테고리 목록 (비어있으면 모든 카테고리)"
    )
    arxiv_filter_mode: Literal["AND", "OR"] = Field(
        default="OR", description="카테고리 필터 모드 (AND: 모두 포함, OR: 하나라도 포함)"
    )

    # HuggingFace 필터
    hf_keywords: List[str] = Field(
        default_factory=list, description="HuggingFace ai_keywords 목록 (비어있으면 필터링 안함)"
    )
    hf_filter_mode: Literal["AND", "OR"] = Field(
        default="OR", description="키워드 필터 모드 (AND: 모두 포함, OR: 하나라도 포함)"
    )
    hf_min_upvotes: int = Field(default=0, ge=0, description="최소 upvote 수 (0이면 필터링 안함)")
    hf_max_papers: int = Field(default=50, ge=1, le=100, description="HF에서 가져올 최대 논문 수")

    # Novelty 필터 (arXiv만 적용)
    novelty_enabled: bool = Field(default=True, description="Novelty ranking 활성화 여부")
    novelty_top_n: int = Field(default=10, ge=1, description="Novelty ranking 후 선택할 논문 수")
    novelty_min_score: Optional[float] = Field(
        default=None, ge=1.0, le=10.0, description="최소 novelty 점수 (None이면 제한 없음)"
    )

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, v: List[str]) -> List[str]:
        """소스 목록이 비어있지 않은지 확인."""
        if not v:
            raise ValueError("적어도 하나의 소스를 선택해야 합니다")
        return v

    def get_date_range(self) -> tuple[datetime, datetime]:
        """날짜 범위를 계산하여 반환."""
        if self.date_from is not None:
            start_date = datetime.combine(self.date_from, datetime.min.time())
        else:
            start_date = datetime.now() - timedelta(days=self.days_back)

        if self.date_to is not None:
            end_date = datetime.combine(self.date_to, datetime.max.time())
        else:
            end_date = datetime.now()

        return start_date, end_date

    class Config:
        json_schema_extra = {
            "example": {
                "sources": ["arxiv", "huggingface"],
                "days_back": 1,
                "arxiv_categories": ["cs.CV", "cs.AI"],
                "arxiv_filter_mode": "OR",
                "hf_keywords": ["computer-vision", "diffusion"],
                "hf_filter_mode": "AND",
                "novelty_enabled": True,
                "novelty_top_n": 10,
            }
        }
