# 리팩토링 진행 상황

**업데이트**: 2025-11-25
**상태**: Phase 1 완료, Phase 2 진행 중

---

## ✅ 완료된 작업

### Phase 1: 프로젝트 구조 및 코어 리팩토링
- [x] **프로젝트 구조 생성**
  - UV 기반 패키지 구조 (`src/paper_review/`)
  - 디렉토리: `core/`, `models/`, `agents/`, `utils/`, `web/`, `cli/`
  - 테스트 디렉토리: `tests/`

- [x] **pyproject.toml 작성**
  - Python 3.12 요구사항
  - 모든 의존성 정의 (FastAPI, Pydantic, httpx 등)
  - Ruff, mypy 설정
  - pytest 설정

- [x] **Pydantic 모델 정의**
  - `PaperMetadata`: arXiv + HuggingFace 통합 메타데이터
  - `Paper`: 전체 논문 데이터 (PDF, 텍스트, 이미지 포함)
  - `NoveltyScore`: Novelty ranking 점수
  - `FilterConfig`: AND/OR 필터링 설정
  - `PaperSummary`, `SummaryReport`: 요약 데이터

### Phase 2: 멀티 소스 Fetcher 구현 (진행 중)
- [x] **BaseAgent 추상 클래스**
  - 모든 에이전트의 베이스
  - Loguru 로깅 통합

- [x] **HuggingFaceFetcher 구현**
  - `https://huggingface.co/api/daily_papers` API 통합
  - Async/await 기반 (httpx)
  - 날짜 필터링
  - AND/OR 키워드 필터링
  - Upvote 필터링
  - 최대 50개 제한

---

## 🚧 진행 중인 작업

### ArxivFetcher 마이그레이션
**필요 작업**:
1. Utils 모듈 마이그레이션
   - `arxiv_client.py` → `src/paper_review/utils/arxiv.py`
   - `pdf_processor.py` → `src/paper_review/utils/pdf.py`
   - `image_extractor.py` → `src/paper_review/utils/image.py`

2. ArxivFetcher 구현
   - 기존 `FetcherAgent` 기반
   - FilterConfig와 통합
   - AND/OR 카테고리 필터링
   - 날짜 범위 필터링

---

## 📋 다음 단계

### 즉시 필요한 작업 (Priority 1)
1. **Utils 마이그레이션** (30분)
   - arxiv_client, pdf_processor, image_extractor
   - 새로운 구조에 맞게 수정

2. **ArxivFetcher 구현** (30분)
   - FilterConfig 통합
   - HuggingFaceFetcher와 일관된 인터페이스

3. **NoveltyRanker 마이그레이션** (20분)
   - 기존 코드 기반
   - arXiv 논문만 적용

4. **통합 Fetcher** (10분)
   - arXiv + HuggingFace 결과 병합
   - 필터링 로직 통합

### 중요 작업 (Priority 2)
5. **간단한 CLI 테스트** (15분)
   - `python -m paper_review.cli fetch` 명령어
   - 기본 동작 확인

6. **FastAPI 웹 인터페이스** (2-3시간)
   - 라우팅 설정
   - Jinja2 템플릿
   - 홈 페이지, 논문 리스트 페이지

### 배포 준비 (Priority 3)
7. **Docker 설정** (1시간)
   - Dockerfile
   - docker-compose.yml (웹 + Ollama)

8. **문서 업데이트** (30분)
   - README.md
   - 사용 가이드

---

## 📁 현재 파일 구조

```
paper-review-service/
├── pyproject.toml              ✅ 완료
├── REFACTORING_PLAN.md         ✅ 완료
├── PROGRESS.md                 ✅ 완료
│
├── src/
│   └── paper_review/
│       ├── __init__.py
│       ├── models/             ✅ 완료
│       │   ├── paper.py
│       │   ├── filters.py
│       │   └── summary.py
│       ├── agents/             ⚠️ 부분 완료
│       │   ├── base.py         ✅
│       │   └── fetcher/
│       │       └── huggingface.py  ✅
│       ├── utils/              ⏳ 대기 중
│       ├── web/                ⏳ 대기 중
│       └── cli/                ⏳ 대기 중
│
├── templates/
│   └── web/                    ⏳ 대기 중
│
├── static/
│   ├── css/                    ⏳ 대기 중
│   └── js/                     ⏳ 대기 중
│
├── config/
│   └── config.yaml             ⏳ 업데이트 필요
│
├── tests/                      ⏳ 대기 중
│
└── data/                       (기존 유지)
```

---

## 💡 주요 설계 결정

1. **Python 3.12** 사용
2. **UV** 패키지 관리자
3. **FastAPI + Jinja2** (서버사이드 렌더링)
4. **Pydantic v2** (데이터 검증)
5. **httpx** (async HTTP 클라이언트)
6. **Loguru** (구조화된 로깅)
7. **AND/OR 필터링** (사용자 선택 가능)
8. **멀티 소스**: arXiv + HuggingFace

---

## 🎯 다음 세션 추천 작업

**Option 1: 빠른 프로토타입 (2-3시간)**
- Utils 마이그레이션
- ArxivFetcher 구현
- 간단한 CLI 테스트
- 기본 동작 확인

**Option 2: 웹 인터페이스 우선 (3-4시간)**
- FastAPI 기본 구조
- 홈 페이지 (필터 폼)
- Mock 데이터로 UI 테스트
- 나중에 백엔드 연결

**Option 3: 단계별 완성 (권장, 4-5시간)**
1. Utils + ArxivFetcher (1시간)
2. NoveltyRanker + Summarizer 마이그레이션 (1시간)
3. FastAPI 웹 인터페이스 (2시간)
4. Docker 설정 (1시간)

---

## ⚠️ 주의사항

1. **기존 코드 호환성**
   - 기존 `data/` 디렉토리는 그대로 유지
   - 기존 config.yaml은 나중에 업데이트

2. **테스트 필요**
   - HuggingFaceFetcher 실제 API 테스트
   - FilterConfig 검증
   - 날짜 범위 계산

3. **UV 설치 필요**
   - 개발 환경에 UV 설치: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - 의존성 설치: `uv sync`

---

**다음에 할 일**: Utils 마이그레이션 또는 FastAPI 웹 인터페이스 중 선택
