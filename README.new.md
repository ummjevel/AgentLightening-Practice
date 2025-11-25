# 📚 Paper Review Service

AI/ML 논문 자동 수집 및 요약 서비스 - arXiv + HuggingFace Daily Papers 통합

## ✨ Features

- 🔍 **멀티 소스 통합**: arXiv + HuggingFace Daily Papers
- 🎯 **지능형 필터링**: AND/OR 조건으로 유연한 논문 검색
- 🤖 **LLM 기반 요약**: Ollama를 사용한 한국어/영어 요약
- 📊 **Novelty Ranking**: arXiv 논문의 참신성/영향력 자동 평가
- 🌐 **웹 인터페이스**: FastAPI + Jinja2 서버사이드 렌더링
- 🐳 **Docker 지원**: 원클릭 배포

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- (선택) Python 3.12 + UV

### 1. Docker Compose로 실행

```bash
# Docker Compose로 시작
docker-compose up -d

# Ollama 모델 설치 (첫 실행 시)
docker exec -it paper-review-ollama ollama pull qwen3:8b

# 웹 인터페이스 접속
open http://localhost:8000
```

### 2. 로컬 개발 환경

```bash
# UV 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync

# Ollama 설치 및 실행
ollama serve
ollama pull qwen3:8b

# 웹 서버 실행
uvicorn paper_review.web.app:app --reload --host 0.0.0.0 --port 8000
```

## 📖 사용 방법

1. 브라우저에서 `http://localhost:8000` 접속
2. 필터 설정 (소스, 카테고리, 키워드, 날짜 등)
3. "논문 검색" 버튼 클릭
4. 결과 확인

## ⚙️ 주요 설정

`config/config.yaml` 파일에서 설정 가능:

- arXiv 카테고리 (cs.CV, cs.AI, eess.AS 등)
- HuggingFace 키워드
- Novelty ranking 옵션
- LLM 모델 및 파라미터

## 🛠️ 기술 스택

- Python 3.12, FastAPI, Pydantic v2
- Ollama (qwen3:8b)
- Docker & Docker Compose

## 📄 License

MIT License
