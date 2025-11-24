# arXiv 논문 요약기

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> *arXiv의 최신 학술 논문을 자동으로 수집하고, AI로 요약하며, 시각화하는 지능형 에이전트 시스템. Agent Lightning 통합을 통한 지속적인 최적화 지원*

**한국어** | [English](README.md)

---

## 🎯 주요 기능

- ✅ **자동 논문 수집**: arXiv API를 통한 최신 논문 자동 다운로드
- ✅ **AI 기반 요약**: SKT-AI A.X-4.0 LLM을 활용한 구조화된 요약
- ✅ **스마트 이미지 추출**: PDF에서 핵심 그림 자동 추출
- ✅ **아름다운 HTML 리포트**: 이미지가 포함된 시각적 보고서 생성
- ✅ **설정 파일 관리**: 중앙화된 YAML 설정 (하드코딩 제로!)
- ⚡ **Agent Lightning 통합**: 강화학습을 통한 에이전트 성능 추적 및 최적화

---

## 📐 아키텍처

이 프로젝트는 [Agent Lightning](https://github.com/microsoft/agent-lightning)에서 영감을 받은 멀티 에이전트 아키텍처를 구현합니다:

```
┌─────────────────────────────────────────────────────────┐
│             arXiv 논문 요약 시스템                        │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Fetcher    │  │ Summarizer   │  │  Presenter   │
│   Agent      │  │   Agent      │  │    Agent     │
│              │  │  (AL 추적*)   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
    arXiv API         LLM (A.X-4.0)      HTML 리포트
                                         + 이미지

* AL = Agent Lightning 추적
```

### 에이전트 설명

| 에이전트 | 역할 | 주요 기능 |
|---------|------|----------|
| **Fetcher** | 논문 수집 및 추출 | PDF 다운로드, 텍스트 및 이미지 추출 |
| **Summarizer** | AI 기반 요약 | LLM을 사용한 구조화된 요약 생성 |
| **Presenter** | 리포트 생성 | 아름다운 HTML 보고서 생성 |

---

## 📁 프로젝트 구조

```
arxiv-paper-summarizer/
├── agents/                      # 에이전트 모듈
│   ├── __init__.py
│   ├── fetcher.py              # 논문 수집 에이전트
│   ├── summarizer.py           # 요약 에이전트 (AL 추적 포함)
│   └── presenter.py            # 리포트 생성 에이전트
├── utils/                       # 유틸리티 모듈
│   ├── __init__.py
│   ├── config_loader.py        # YAML 설정 로더
│   ├── arxiv_client.py         # arXiv API 클라이언트
│   ├── pdf_processor.py        # PDF 텍스트 추출
│   ├── image_extractor.py      # PDF 이미지 추출
│   └── agent_lightning_tracker.py  # Agent Lightning 통합
├── templates/                   # HTML 템플릿
│   └── summary_report.html     # 리포트 템플릿
├── config/                      # 설정 파일
│   └── config.yaml             # 메인 설정 파일
├── data/                        # 데이터 저장소
│   ├── papers/                 # 다운로드된 PDF
│   ├── images/                 # 추출된 이미지
│   ├── summaries/              # 생성된 리포트
│   └── lightning_store/        # Agent Lightning 추적 데이터
├── main.py                      # 메인 실행 파일
├── requirements.txt             # Python 의존성
├── README.md                    # 영어 문서
└── README.ko.md                 # 한국어 문서
```

---

## 🚀 빠른 시작

### 필수 요구사항

- Python 3.9 이상
- pip (Python 패키지 관리자)

### 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/arxiv-paper-summarizer.git
cd arxiv-paper-summarizer

# 의존성 설치
pip install -r requirements.txt
```

### 설정

모든 설정은 `config/config.yaml`에서 관리됩니다:

```yaml
# arXiv 설정
arxiv:
  category: "eess.AS"        # 논문 카테고리
  max_results: 10            # 가져올 논문 수

# LLM 설정 (SKT-AI A.X-4.0)
llm:
  api_key: "your-api-key"    # API 키
  model: "ax4"               # 모델명
  temperature: 0.7           # 생성 온도

# Agent Lightning 설정 (선택사항)
agent_lightning:
  enabled: false             # 추적 활성화/비활성화
  track_prompts: true
  track_responses: true
  track_rewards: true
```

### 실행

```bash
python main.py
```

**참고**: arXiv API는 때때로 rate limiting이나 일시적인 접근 제한이 있을 수 있습니다. HTTP 403 오류가 발생하면 몇 분 후에 다시 시도하거나, 다른 네트워크 환경에서 실행해보세요.

---

## ⚡ Agent Lightning 통합

이 프로젝트는 강화학습을 통한 에이전트 성능 최적화를 위한 [Agent Lightning](https://github.com/microsoft/agent-lightning) 통합을 선택적으로 지원합니다.

### Agent Lightning이란?

Agent Lightning은 Microsoft의 AI 에이전트 최적화 프레임워크로, 최소한의 코드 변경으로 다음을 제공합니다:

- **자동 추적**: 프롬프트, 응답, 보상 자동 기록
- **강화학습**: 반복적인 성능 개선
- **프롬프트 최적화**: 다양한 알고리즘을 통한 최적화
- **프레임워크 독립적**: 모든 에이전트 프레임워크와 호환

### Agent Lightning 활성화

1. **Agent Lightning 설치** (`requirements.txt`에서 주석 해제):
   ```bash
   pip install agentlightning
   ```

2. **설정에서 활성화** (`config/config.yaml`):
   ```yaml
   agent_lightning:
     enabled: true
     store_path: "data/lightning_store"
     track_prompts: true
     track_responses: true
     track_rewards: true
     optimization_algorithm: "rl"
   ```

3. **시스템 실행**:
   ```bash
   python main.py
   ```

### 작동 원리

**SummarizerAgent**에 Agent Lightning 추적이 포함되어 있습니다:

```python
# 프롬프트 추적
event_id = tracker.emit_prompt(
    agent_name="SummarizerAgent",
    prompt=prompt,
    metadata={'paper_id': paper_id, 'model': self.model}
)

# 응답 추적
tracker.emit_response(
    event_id=event_id,
    response=summary_text,
    metadata={'tokens_used': tokens}
)

# 보상 추적 (품질 휴리스틱 기반)
tracker.emit_reward(
    event_id=event_id,
    reward=0.8,
    reason="좋은 요약 길이와 구조"
)
```

### 추적 데이터

모든 추적 데이터는 `data/lightning_store/session_*.json`에 저장됩니다:

```json
{
  "session_id": "20241124_120000",
  "total_events": 42,
  "events": [
    {
      "event_type": "prompt",
      "agent_name": "SummarizerAgent",
      "prompt": "...",
      "metadata": {...}
    },
    {
      "event_type": "response",
      "response": "...",
      "metadata": {...}
    },
    {
      "event_type": "reward",
      "reward": 0.8,
      "reason": "..."
    }
  ]
}
```

---

## 📋 설정 가이드

### arXiv 설정

| 매개변수 | 설명 | 기본값 |
|---------|------|--------|
| `category` | arXiv 카테고리 코드 | `eess.AS` |
| `max_results` | 가져올 논문 수 | `10` |
| `sort_by` | 정렬 기준 | `submittedDate` |

**인기 카테고리**:
- `cs.AI` - 인공지능
- `cs.CV` - 컴퓨터 비전
- `cs.CL` - 자연어 처리
- `eess.AS` - 오디오 및 음성 처리

### LLM 설정

| 매개변수 | 설명 | 기본값 |
|---------|------|--------|
| `api_key` | SKT-AI API 키 | 필수 |
| `base_url` | API 엔드포인트 | `https://guest-api.sktax.chat/v1` |
| `model` | 모델명 | `ax4` |
| `temperature` | 생성 온도 | `0.7` |
| `max_tokens` | 최대 응답 토큰 수 | `2000` |

### PDF 처리 설정

| 매개변수 | 설명 | 기본값 |
|---------|------|--------|
| `max_images_per_paper` | 논문당 추출할 이미지 수 | `3` |
| `image_format` | 출력 이미지 형식 | `png` |
| `min_image_width` | 최소 이미지 너비 | `300` |
| `min_image_height` | 최소 이미지 높이 | `300` |

---

## 📊 출력 예시

생성된 HTML 리포트는 다음을 포함합니다:

### 1. 논문 메타데이터
- 제목, 저자, 제출일
- arXiv ID 및 직접 링크
- 카테고리

### 2. 구조화된 요약
- 📋 **한눈에 보기**: 2-3문장 개요
- 🎯 **연구 목적**: 해결하고자 하는 문제
- 🔬 **방법론**: 사용된 핵심 기술
- 📊 **주요 결과**: 핵심 발견사항
- 💡 **의의 및 영향**: 학문적/실용적 가치

### 3. 주요 그림
- PDF에서 추출한 2-3개의 주요 그림
- 각 그림의 캡션

**예시 출력**: `data/summaries/2024-11-24-arxiv-summary.html`

---

## 🛠️ 개발

### 새 카테고리 추가

`config/config.yaml`을 편집하세요:

```yaml
arxiv:
  category: "cs.AI"  # 원하는 카테고리로 변경
```

### 템플릿 커스터마이징

리포트 디자인을 변경하려면 `templates/summary_report.html`을 수정하세요.

### 로깅 설정

`config/config.yaml`에서 로깅을 설정하세요:

```yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
  file: "arxiv_summarizer.log"
```

---

## 🧪 테스트

```bash
# 테스트 설정으로 실행 (2개 논문)
# config.yaml에서 max_results: 2로 설정
python main.py

# 출력 확인
ls data/summaries/
```

---

## 🤝 기여하기

기여를 환영합니다! Pull Request를 자유롭게 제출해주세요.

1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 열기

---

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🙏 감사의 글

- [arXiv](https://arxiv.org/) - 오픈 액세스 사전 출판 저장소
- [SKT-AI](https://github.com/SKT-AI/A.X-4.0) - A.X-4.0 LLM API 제공
- [Agent Lightning](https://github.com/microsoft/agent-lightning) - AI 에이전트 최적화 프레임워크
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF 처리 라이브러리

---

## 📞 지원

- 이슈: [GitHub Issues](https://github.com/yourusername/arxiv-paper-summarizer/issues)
- 문서: [Wiki](https://github.com/yourusername/arxiv-paper-summarizer/wiki)

---

## 🗺️ 로드맵

- [ ] 다양한 LLM 제공자 지원 (OpenAI, Claude 등)
- [ ] 다국어 요약 지원
- [ ] 일일 다이제스트 이메일 알림
- [ ] 설정용 웹 인터페이스
- [ ] 완전한 Agent Lightning 최적화 파이프라인
- [ ] Docker 컨테이너화

---

커뮤니티가 ❤️로 만들었습니다
