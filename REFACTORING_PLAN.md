# Paper Review Service - 리팩토링 및 기능 추가 기획

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [현재 상태 분석](#현재-상태-분석)
3. [리팩토링 계획](#리팩토링-계획)
4. [신규 기능: HuggingFace Daily Papers](#신규-기능-huggingface-daily-papers)
5. [고급 필터링 시스템](#고급-필터링-시스템)
6. [구현 로드맵](#구현-로드맵)
7. [기술 스택](#기술-스택)

---

## 🎯 프로젝트 개요

### 비전
다양한 소스(arXiv, HuggingFace)에서 AI/ML 논문을 자동으로 수집, 필터링, 요약하여 매일 최신 연구 동향을 한눈에 파악할 수 있는 서비스

### 핵심 가치
- **자동화**: 매일 자동으로 논문 수집 및 요약
- **지능형 필터링**: LLM 기반 중요도 평가로 핵심 논문만 선별
- **다중 소스 통합**: arXiv + HuggingFace Daily Papers 통합
- **유연한 분류**: 분야별, 태그별 세부 필터링
- **로컬 우선**: Ollama 사용으로 API 비용 제로

---

## 🔍 현재 상태 분석

### 강점
- ✅ 안정적인 멀티 에이전트 아키텍처
- ✅ 2단계 파이프라인 (메타데이터 수집 → 필터링 → 상세 처리)
- ✅ LLM 기반 novelty ranking 시스템
- ✅ 완전한 YAML 설정 시스템
- ✅ Ollama 통합으로 외부 API 의존성 제거
- ✅ 멀티모달 분석 지원 (텍스트 + 이미지)

### 개선 필요 사항
- ⚠️ 패키지 구조 미비 (uv 기반 패키징 필요)
- ⚠️ 단일 소스 (arXiv만 지원)
- ⚠️ 제한적인 필터링 (카테고리 하나만 선택 가능)
- ⚠️ CLI 전용 (API/웹 인터페이스 없음)
- ⚠️ 테스트 코드 부재
- ⚠️ 데이터 모델 명시화 부족 (딕셔너리 기반)

---

## 🏗️ 리팩토링 계획

### 1. UV 기반 패키지 구조화

#### 새로운 디렉토리 구조
```
paper-review-service/
├── pyproject.toml              # UV 프로젝트 설정
├── README.md                   # 영문 문서
├── README.ko.md                # 한글 문서
├── LICENSE
├── .gitignore
│
├── src/
│   └── paper_review/
│       ├── __init__.py
│       ├── __main__.py         # CLI 진입점
│       │
│       ├── core/               # 핵심 로직
│       │   ├── __init__.py
│       │   ├── config.py       # 설정 관리
│       │   ├── pipeline.py     # 메인 파이프라인
│       │   └── exceptions.py   # 커스텀 예외
│       │
│       ├── models/             # 데이터 모델 (Pydantic)
│       │   ├── __init__.py
│       │   ├── paper.py        # Paper, Metadata 스키마
│       │   ├── summary.py      # Summary 스키마
│       │   └── filters.py      # FilterConfig 스키마
│       │
│       ├── agents/             # 멀티 에이전트
│       │   ├── __init__.py
│       │   ├── base.py         # BaseAgent 추상 클래스
│       │   ├── fetcher/
│       │   │   ├── __init__.py
│       │   │   ├── arxiv.py    # ArxivFetcher
│       │   │   └── huggingface.py  # HuggingFaceFetcher
│       │   ├── ranker.py       # NoveltyRanker
│       │   ├── summarizer.py   # SummarizerAgent
│       │   └── presenter.py    # PresenterAgent
│       │
│       ├── utils/              # 유틸리티
│       │   ├── __init__.py
│       │   ├── pdf.py          # PDF 처리
│       │   ├── image.py        # 이미지 추출
│       │   ├── llm.py          # LLM 클라이언트 (Ollama)
│       │   └── logging.py      # 로깅 설정
│       │
│       └── cli/                # CLI 인터페이스
│           ├── __init__.py
│           ├── commands.py     # Click 명령어
│           └── formatting.py   # 출력 포맷팅
│
├── config/
│   ├── config.yaml             # 기본 설정
│   └── config.example.yaml     # 예제 설정
│
├── templates/
│   ├── report.html             # HTML 리포트
│   └── email.html              # 이메일 템플릿 (미래)
│
├── tests/                      # 테스트 코드
│   ├── __init__.py
│   ├── conftest.py             # pytest 설정
│   ├── test_agents/
│   ├── test_utils/
│   └── test_integration/
│
└── data/                       # 런타임 데이터 (gitignore)
    ├── papers/
    ├── images/
    └── summaries/
```

#### pyproject.toml 구조
```toml
[project]
name = "paper-review-service"
version = "0.2.0"
description = "AI/ML 논문 자동 수집 및 요약 서비스"
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

dependencies = [
    "arxiv>=2.3.1",
    "pyyaml>=6.0.1",
    "requests>=2.32.0",
    "pymupdf>=1.26.0",
    "pillow>=12.0.0",
    "jinja2>=3.1.6",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "click>=8.1.0",
    "rich>=13.9.0",
    "loguru>=0.7.0",
    "huggingface-hub>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[project.scripts]
paper-review = "paper_review.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

### 2. 코드 개선 사항

#### A. Pydantic 모델 도입
```python
# src/paper_review/models/paper.py
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional

class PaperMetadata(BaseModel):
    """논문 메타데이터"""
    title: str
    authors: List[str]
    summary: str
    published: date
    arxiv_id: Optional[str] = None
    primary_category: str
    categories: List[str]
    source: str = Field(description="arxiv or huggingface")
    tags: List[str] = Field(default_factory=list)

class Paper(BaseModel):
    """전체 논문 데이터"""
    metadata: PaperMetadata
    pdf_path: Optional[str] = None
    full_text: Optional[str] = None
    image_paths: List[str] = Field(default_factory=list)
    novelty_score: Optional[dict] = None
```

#### B. BaseAgent 추상 클래스
```python
# src/paper_review/agents/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """모든 에이전트의 베이스 클래스"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logger()

    @abstractmethod
    def execute(self, *args, **kwargs):
        """에이전트 실행 메서드"""
        pass

    def _setup_logger(self):
        """로거 설정"""
        from loguru import logger
        return logger.bind(agent=self.__class__.__name__)
```

#### C. Click 기반 CLI
```python
# src/paper_review/cli/commands.py
import click
from rich.console import Console

@click.group()
@click.version_option(version="0.2.0")
def main():
    """Paper Review Service CLI"""
    pass

@main.command()
@click.option("--source", type=click.Choice(["arxiv", "huggingface", "all"]),
              default="all", help="논문 소스")
@click.option("--category", multiple=True, help="arXiv 카테고리 (여러 개 가능)")
@click.option("--tag", multiple=True, help="HuggingFace 태그 (여러 개 가능)")
@click.option("--top-n", default=10, help="선별할 논문 수")
def fetch(source, category, tag, top_n):
    """논문 수집 및 요약 생성"""
    console = Console()
    console.print(f"[green]Fetching papers from: {source}[/green]")
    # ... 실행 로직
```

---

## 🤗 신규 기능: HuggingFace Daily Papers

### 기능 개요
HuggingFace의 Daily Papers API를 통해 최신 논문 수집 및 통합

### API 엔드포인트
```
GET https://huggingface.co/api/daily_papers?limit=50
```

### 실제 응답 구조 (확인됨)
```json
[
  {
    "paper": {
      "id": "2511.14899",
      "title": "Paper Title",
      "authors": [
        {
          "_id": "...",
          "name": "Author Name",
          "user": {...}
        }
      ],
      "publishedAt": "2025-11-18T20:37:52.000Z",
      "submittedOnDailyAt": "2025-11-24T10:04:20.120Z",
      "summary": "Paper abstract...",
      "upvotes": 8,
      "ai_keywords": ["keyword1", "keyword2"],
      "githubRepo": "https://github.com/...",
      "projectPage": "https://...",
      "githubStars": 1
    },
    "thumbnail": "https://cdn-thumbnails.huggingface.co/...",
    "numComments": 2,
    "submittedBy": {...},
    "isAuthorParticipating": true
  }
]
```

### 구현 설계

#### A. HuggingFaceFetcher 클래스
```python
# src/paper_review/agents/fetcher/huggingface.py
from typing import List
from paper_review.models.paper import Paper, PaperMetadata
from paper_review.agents.base import BaseAgent

class HuggingFaceFetcher(BaseAgent):
    """HuggingFace Daily Papers 수집 에이전트"""

    def __init__(self, config):
        super().__init__(config)
        self.api_url = "https://huggingface.co/api/daily_papers"
        self.session = requests.Session()

    def fetch_daily_papers(self,
                          days_back: int = 1,
                          min_upvotes: int = 5,
                          tags_filter: List[str] = None) -> List[Paper]:
        """
        HF Daily Papers 수집

        Args:
            days_back: 며칠 전까지 가져올지
            min_upvotes: 최소 upvote 수
            tags_filter: 필터링할 태그 목록 (OR 조건)
        """
        response = self.session.get(self.api_url)
        response.raise_for_status()

        papers_data = response.json()["papers"]
        papers = []

        for paper_data in papers_data:
            # 태그 필터링
            if tags_filter and not any(tag in paper_data["tags"] for tag in tags_filter):
                continue

            # Upvote 필터링
            if paper_data["upvotes"] < min_upvotes:
                continue

            metadata = PaperMetadata(
                title=paper_data["title"],
                authors=paper_data["authors"],
                summary=paper_data["abstract"],
                published=paper_data["published_at"],
                arxiv_id=paper_data.get("arxiv_id"),
                primary_category=paper_data["tags"][0] if paper_data["tags"] else "unknown",
                categories=paper_data["tags"],
                source="huggingface",
                tags=paper_data["tags"]
            )

            papers.append(Paper(metadata=metadata))

        return papers

    def execute(self, **kwargs):
        return self.fetch_daily_papers(**kwargs)
```

#### B. 설정 추가
```yaml
# config/config.yaml
huggingface:
  enabled: true
  max_papers: 50                  # 최대 논문 수 (HF는 novelty ranking 없이 다 가져오기)
  date_range_days: 1              # 최근 N일 이내 논문만
  keywords_filter: []             # ai_keywords 필터 (비어있으면 필터링 안함)
    # 예: ["computer-vision", "diffusion"]
  filter_mode: "OR"               # "AND" 또는 "OR"
  min_upvotes: 0                  # 최소 upvote 수 (0이면 필터링 안함)

# arXiv 설정도 filter_mode 추가
arxiv:
  category: "cs.LG"
  categories: ["cs.CV", "cs.AI", "cs.LG", "eess.AS"]  # 여러 카테고리 (비어있으면 category 사용)
  filter_mode: "OR"               # "AND" 또는 "OR"
  max_results: 1000
  sort_by: "submittedDate"
  sort_order: "descending"
```

---

## 🔍 고급 필터링 시스템

### 1. 다중 소스 통합 필터링

#### 필터 우선순위
```
1. Source Filter (arxiv, huggingface, all)
   ↓
2. Date Filter (최근 N일 이내)
   ↓
3. Category/Keyword Filter (AND/OR 선택 가능)
   - arXiv: 카테고리 필터 (AND: 모두 포함, OR: 하나라도 포함)
   - HuggingFace: ai_keywords 필터 (AND: 모두 포함, OR: 하나라도 포함)
   ↓
4. Novelty Ranking (arXiv만, LLM-based scoring)
   ↓
5. Top-N Selection (arXiv만)
   HuggingFace는 필터링 후 max 50개까지 모두 가져오기
```

#### 필터 설정 모델
```python
# src/paper_review/models/filters.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import date

class FilterConfig(BaseModel):
    """필터링 설정"""

    # 소스 필터
    sources: List[Literal["arxiv", "huggingface"]] = ["arxiv", "huggingface"]

    # 날짜 필터
    date_from: Optional[date] = None  # None이면 days_back 사용
    date_to: Optional[date] = None
    days_back: int = 1  # 최근 N일 (date_from/date_to가 None일 때 사용)

    # arXiv 필터
    arxiv_categories: List[str] = []  # 비어있으면 모든 카테고리
    arxiv_filter_mode: Literal["AND", "OR"] = "OR"
    # AND: ["cs.CV", "cs.AI"] → 두 카테고리 모두 포함된 논문만
    # OR: ["cs.CV", "cs.AI"] → 하나라도 포함된 논문

    # HuggingFace 필터
    hf_keywords: List[str] = []  # 비어있으면 필터링 안함
    hf_filter_mode: Literal["AND", "OR"] = "OR"
    # AND: ["computer-vision", "diffusion"] → 두 키워드 모두 포함
    # OR: ["computer-vision", "diffusion"] → 하나라도 포함
    hf_min_upvotes: int = 0  # 0이면 필터링 안함
    hf_max_papers: int = 50  # 최대 50개

    # Novelty 필터 (arXiv만 적용)
    novelty_enabled: bool = True
    novelty_top_n: int = 10
```

### 2. 카테고리 및 태그 매핑

#### arXiv 카테고리 → HF 태그 매핑
```python
CATEGORY_TAG_MAPPING = {
    "cs.CV": ["computer-vision", "image-classification", "object-detection"],
    "cs.CL": ["natural-language-processing", "text-generation", "translation"],
    "cs.LG": ["machine-learning", "deep-learning", "reinforcement-learning"],
    "cs.AI": ["artificial-intelligence", "agents", "reasoning"],
    "eess.AS": ["audio", "speech-recognition", "audio-classification", "audio-to-audio"],
    "cs.SD": ["audio", "speech", "sound"],  # Sound (arXiv에서는 cs.SD도 오디오 관련)
}
```

#### 주요 arXiv 카테고리 목록
- **cs.CV**: Computer Vision
- **cs.CL**: Computation and Language (NLP)
- **cs.LG**: Machine Learning
- **cs.AI**: Artificial Intelligence
- **cs.SD**: Sound
- **eess.AS**: Audio and Speech Processing
- **cs.RO**: Robotics
- **cs.HC**: Human-Computer Interaction
```

### 3. AND/OR 필터링 로직

#### 필터 적용 함수
```python
def filter_papers(papers: List[Paper], config: FilterConfig) -> List[Paper]:
    """필터링 조건에 따라 논문 필터링"""
    filtered = []

    for paper in papers:
        # arXiv 카테고리 필터
        if paper.metadata.source == "arxiv" and config.arxiv_categories:
            if config.arxiv_filter_mode == "AND":
                # 모든 카테고리가 포함되어야 함
                if not all(cat in paper.metadata.categories for cat in config.arxiv_categories):
                    continue
            else:  # OR
                # 하나라도 포함되면 OK
                if not any(cat in paper.metadata.categories for cat in config.arxiv_categories):
                    continue

        # HuggingFace 키워드 필터
        if paper.metadata.source == "huggingface" and config.hf_keywords:
            if config.hf_filter_mode == "AND":
                # 모든 키워드가 포함되어야 함
                if not all(kw in paper.metadata.tags for kw in config.hf_keywords):
                    continue
            else:  # OR
                # 하나라도 포함되면 OK
                if not any(kw in paper.metadata.tags for kw in config.hf_keywords):
                    continue

        # 날짜 필터
        if not is_within_date_range(paper.metadata.published, config):
            continue

        filtered.append(paper)

    return filtered
```

### 4. 고급 Novelty Ranking

#### 소스별 가중치 적용 (미래 기능)
```python
def calculate_weighted_score(paper: Paper) -> float:
    """
    소스별 가중치를 반영한 최종 점수 계산

    - HuggingFace: upvote 수 반영 (+0.5 per 10 upvotes)
    - arXiv: citation count (미래 기능)
    """
    base_score = paper.novelty_score["total_score"]

    if paper.metadata.source == "huggingface":
        # HF upvote 보너스
        upvote_bonus = min(paper.metadata.upvotes / 10 * 0.5, 2.0)
        return base_score + upvote_bonus

    return base_score
```

### 5. 웹 인터페이스 (FastAPI + SSR)

#### 주요 페이지
1. **홈 페이지** (`/`)
   - 필터 설정 폼
   - 최근 생성된 리포트 목록

2. **논문 리스트** (`/papers`)
   - GET 파라미터로 필터 전달
   - 서버사이드에서 렌더링된 논문 카드
   - 페이지네이션

3. **논문 상세** (`/papers/{arxiv_id}`)
   - 요약 전문
   - 이미지
   - 원문 링크

4. **API 엔드포인트** (`/api/fetch`)
   - 백그라운드에서 논문 수집 시작
   - SSE(Server-Sent Events)로 진행상황 전달

#### 예시 라우트
```python
# src/paper_review/web/routes.py
@app.get("/")
async def home(request: Request):
    """홈 페이지 - 필터 설정 폼"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/papers")
async def list_papers(
    request: Request,
    source: str = "all",
    arxiv_categories: str = "",
    hf_keywords: str = "",
    days_back: int = 1
):
    """필터링된 논문 리스트 (SSR)"""
    # 필터링 로직
    papers = await fetch_and_filter_papers(...)
    return templates.TemplateResponse(
        "papers.html",
        {"request": request, "papers": papers}
    )

@app.post("/api/fetch")
async def fetch_papers(background_tasks: BackgroundTasks, filters: FilterConfig):
    """논문 수집 시작 (백그라운드)"""
    background_tasks.add_task(run_pipeline, filters)
    return {"status": "started"}
```

---

## 📅 구현 로드맵

### Phase 1: 프로젝트 구조 및 코어 리팩토링 (1일)
- [x] 현재 코드 분석 완료
- [x] HuggingFace API 확인 완료
- [ ] UV 기반 프로젝트 구조 생성
  - [ ] pyproject.toml 설정
  - [ ] src/ 디렉토리 구조
  - [ ] Docker 및 Docker Compose 설정
- [ ] Pydantic 모델 정의
  - [ ] Paper, PaperMetadata 모델
  - [ ] FilterConfig 모델
  - [ ] Summary 모델
- [ ] 기존 코드 마이그레이션
  - [ ] utils/ 마이그레이션 (PDF, 이미지, LLM)
  - [ ] config 시스템 개선 (Pydantic Settings)

### Phase 2: 멀티 소스 Fetcher 구현 (1일)
- [ ] ArxivFetcher 마이그레이션 및 개선
- [ ] HuggingFaceFetcher 신규 구현
  - [ ] API 클라이언트 (httpx)
  - [ ] 날짜 필터링
  - [ ] AND 조건 키워드 필터링
  - [ ] 최대 50개 제한
- [ ] NoveltyRanker 마이그레이션 (arXiv만 적용)
- [ ] SummarizerAgent 마이그레이션
- [ ] PresenterAgent 마이그레이션

### Phase 3: FastAPI 웹 인터페이스 (1-1.5일)
- [ ] FastAPI 애플리케이션 구조
  - [ ] 라우팅 설정
  - [ ] Jinja2 템플릿 설정
  - [ ] 정적 파일 서빙
- [ ] 웹 페이지 구현
  - [ ] 홈 페이지 (필터 폼)
  - [ ] 논문 리스트 페이지 (SSR)
  - [ ] 논문 상세 페이지
- [ ] API 엔드포인트
  - [ ] POST /api/fetch (백그라운드 작업)
  - [ ] GET /api/status (진행상황)
  - [ ] GET /api/papers (JSON)
- [ ] 프론트엔드 (기본 CSS)
  - [ ] 반응형 레이아웃
  - [ ] 필터 폼 UI
  - [ ] 논문 카드 디자인

### Phase 4: Docker 및 배포 준비 (0.5일)
- [ ] Dockerfile 작성
- [ ] docker-compose.yml 작성
  - [ ] 웹 서비스
  - [ ] Ollama 서비스
  - [ ] 볼륨 마운트 (data/, config/)
- [ ] 환경 변수 설정
- [ ] README 업데이트
  - [ ] 설치 방법
  - [ ] Docker 실행 방법
  - [ ] API 문서
  - [ ] 사용 예시

### Phase 5: 테스트 및 최적화 (0.5일)
- [ ] 기본 테스트 코드
  - [ ] Fetcher 테스트
  - [ ] Filtering 테스트
  - [ ] API 엔드포인트 테스트
- [ ] 성능 최적화
  - [ ] 비동기 처리 (httpx, asyncio)
  - [ ] 캐싱 전략
- [ ] 문서화 완료

---

## 🛠️ 기술 스택

### 코어
- **Python**: 3.12
- **패키지 관리**: UV
- **설정 관리**: PyYAML, Pydantic Settings
- **로깅**: Loguru

### 웹 프레임워크
- **백엔드**: FastAPI
- **템플릿**: Jinja2 (서버사이드 렌더링)
- **ASGI 서버**: Uvicorn
- **정적 파일**: FastAPI StaticFiles

### 데이터 처리
- **PDF**: PyMuPDF (fitz)
- **이미지**: Pillow
- **HTTP 클라이언트**: httpx (async)

### LLM & API
- **LLM**: Ollama (로컬)
- **arXiv API**: arxiv-py
- **HuggingFace API**: `https://huggingface.co/api/daily_papers`

### 배포
- **컨테이너**: Docker, Docker Compose
- **프로세스 관리**: Supervisor (optional)

### 개발 도구
- **테스트**: pytest, pytest-cov, pytest-asyncio
- **린트**: Ruff
- **타입 체크**: mypy

---

## 🎨 사용자 시나리오

### 시나리오 1: CV 연구자 (웹 인터페이스)
1. 웹 브라우저에서 `http://localhost:8000` 접속
2. 필터 설정:
   - 소스: arXiv + HuggingFace ☑️
   - arXiv 카테고리: cs.CV, cs.AI
   - arXiv 필터 모드: OR (하나라도 포함) 🔘
   - HF 키워드: computer-vision, diffusion
   - HF 필터 모드: AND (모두 포함) 🔘
   - 날짜: 최근 1일
3. "논문 가져오기" 버튼 클릭
4. 실시간 진행상황 확인
5. 완료 후 논문 리스트 확인 (arXiv: 상위 10개, HF: 최대 50개)

### 시나리오 2: NLP 연구자 (Docker 실행)
```bash
# Docker Compose로 서비스 시작
docker-compose up -d

# 웹 브라우저에서 필터 설정
# - 소스: HuggingFace만
# - HF 키워드: natural-language-processing
# - 날짜: 최근 2일
# 결과: 최대 50개 논문 + 요약
```

### 시나리오 3: 오디오/음성 연구자 (특정 도메인)
```
필터 설정:
- 소스: arXiv + HuggingFace ☑️
- arXiv 카테고리: eess.AS, cs.SD
- arXiv 필터 모드: OR (하나라도 포함) 🔘
- HF 키워드: audio, speech-recognition
- HF 필터 모드: OR (하나라도 포함) 🔘
- 날짜: 최근 2일

결과: 오디오 및 음성 처리 관련 최신 논문
```

### 시나리오 4: 일반 AI 동향 파악 (매일 자동화)
```bash
# Cron 작업 설정 (매일 오전 9시)
# 0 9 * * * docker exec paper-review-web python -m paper_review fetch --all

# 웹에서 결과 확인
# http://localhost:8000/papers
```

---

## 📝 추가 고려사항

### MVP 범위 (현재 구현)
- [x] FastAPI 웹 인터페이스 (SSR)
- [x] Docker 기반 배포
- [x] 멀티 소스 통합 (arXiv + HuggingFace)
- [x] AND 조건 필터링
- [x] 날짜 필터링
- [x] LLM 기반 요약 (Ollama)
- [x] 백그라운드 작업 처리

### 미래 기능 (v0.3+)
- [ ] 사용자 인증 및 개인 설정 저장
- [ ] 논문 북마크 및 관리
- [ ] 이메일/Slack/Discord 알림
- [ ] 벡터 DB 통합 (semantic search)
- [ ] 논문 비교 분석
- [ ] React 프론트엔드 (SPA)
- [ ] 멀티 LLM 지원 (OpenAI, Anthropic)
- [ ] RSS 피드 생성

### 배포 및 운영
- Docker Compose로 로컬/프로덕션 환경
- GitHub Actions CI/CD (선택)
- 환경 변수로 설정 관리
- 로그 rotation 및 모니터링

---

## ✅ 최종 확인 사항

### 확인 완료
- [x] **Python 버전**: 3.12
- [x] **프로젝트 구조**: UV 기반 패키지 구조
- [x] **HuggingFace API**: `https://huggingface.co/api/daily_papers` 확인 완료
- [x] **필터링 로직**: AND 조건
- [x] **HF 처리**: novelty ranking 없이 최대 50개
- [x] **날짜 필터**: days_back 파라미터
- [x] **웹 프레임워크**: FastAPI + Jinja2 (SSR)
- [x] **배포**: Docker + Docker Compose

### 구현 스코프
총 예상 기간: **3.5-4일**
- Phase 1: 1일 (프로젝트 구조)
- Phase 2: 1일 (멀티 소스 구현)
- Phase 3: 1-1.5일 (웹 인터페이스)
- Phase 4: 0.5일 (Docker)
- Phase 5: 0.5일 (테스트)

---

**작성일**: 2025-11-25
**버전**: 2.0
**상태**: 승인 대기 중
