# arXiv Paper Summarizer

매일 올라오는 arXiv 논문을 자동으로 수집하고, AI를 활용하여 핵심 내용을 요약하며, 주요 그림과 함께 시각적으로 제공하는 에이전트 시스템입니다.

## 🎯 주요 기능

- ✅ **자동 논문 수집**: arXiv API를 통해 최신 논문 자동 다운로드
- ✅ **AI 요약**: SKT-AI A.X-4.0 LLM을 활용한 구조화된 논문 요약
- ✅ **이미지 추출**: PDF에서 주요 그림 자동 추출
- ✅ **시각적 리포트**: 아름다운 HTML 리포트 자동 생성
- ✅ **설정 파일 관리**: 모든 설정을 YAML 파일로 중앙 관리

## 📁 프로젝트 구조

```
arxiv-summarizer/
├── agents/                      # 에이전트 모듈
│   ├── __init__.py
│   ├── fetcher.py              # 논문 수집 에이전트
│   ├── summarizer.py           # 요약 에이전트
│   └── presenter.py            # 프레젠테이션 에이전트
├── utils/                       # 유틸리티 모듈
│   ├── __init__.py
│   ├── config_loader.py        # 설정 파일 로더
│   ├── arxiv_client.py         # arXiv API 클라이언트
│   ├── pdf_processor.py        # PDF 처리 유틸리티
│   └── image_extractor.py      # 이미지 추출 유틸리티
├── templates/                   # HTML 템플릿
│   └── summary_report.html     # 리포트 템플릿
├── config/                      # 설정 파일
│   └── config.yaml             # 메인 설정 파일
├── data/                        # 데이터 디렉토리
│   ├── papers/                 # 다운로드된 PDF
│   ├── images/                 # 추출된 이미지
│   └── summaries/              # 생성된 요약 리포트
├── main.py                      # 메인 실행 파일
├── requirements.txt             # Python 의존성
└── README.md                    # 문서

```

## 🚀 시작하기

### 1. 필수 요구사항

- Python 3.9 이상
- pip (Python 패키지 관리자)

### 2. 설치

```bash
# 저장소 클론
git clone <repository-url>
cd AgentLightening-Practice

# 의존성 설치
pip install -r requirements.txt
```

### 3. 설정

`config/config.yaml` 파일에서 다음 설정을 조정할 수 있습니다:

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

# 출력 설정
output:
  format: "html"             # 출력 형식
```

### 4. 실행

```bash
python main.py
```

**참고**: arXiv API는 때때로 rate limiting이나 일시적인 접근 제한이 있을 수 있습니다. HTTP 403 오류가 발생하면 몇 분 후에 다시 시도하거나, 다른 네트워크 환경에서 실행해보세요.

## 📋 설정 파일 가이드

### arXiv 설정

| 항목 | 설명 | 기본값 |
|------|------|--------|
| `category` | arXiv 카테고리 | `eess.AS` |
| `max_results` | 가져올 논문 수 | `10` |
| `sort_by` | 정렬 기준 | `submittedDate` |

### LLM 설정

| 항목 | 설명 | 기본값 |
|------|------|--------|
| `api_key` | SKT-AI API 키 | 설정 필요 |
| `base_url` | API 엔드포인트 | `https://guest-api.sktax.chat/v1` |
| `model` | 모델명 | `ax4` |
| `temperature` | 생성 온도 | `0.7` |
| `max_tokens` | 최대 토큰 수 | `2000` |

### PDF 처리 설정

| 항목 | 설명 | 기본값 |
|------|------|--------|
| `max_images_per_paper` | 논문당 추출할 이미지 수 | `3` |
| `image_format` | 이미지 형식 | `png` |
| `min_image_width` | 최소 이미지 너비 | `300` |
| `min_image_height` | 최소 이미지 높이 | `300` |

## 🎨 출력 예시

생성된 HTML 리포트는 다음 정보를 포함합니다:

1. **논문 메타데이터**
   - 제목, 저자, 제출일
   - arXiv ID 및 링크
   - 카테고리

2. **구조화된 요약**
   - 📋 한눈에 보기
   - 🎯 연구 목적
   - 🔬 방법론
   - 📊 주요 결과
   - 💡 의의 및 영향

3. **주요 그림**
   - PDF에서 추출한 핵심 이미지
   - 각 그림의 캡션

## 🤖 Agent 아키텍처

### Fetcher Agent
- arXiv API를 통한 논문 검색 및 다운로드
- PDF에서 텍스트 및 이미지 추출

### Summarizer Agent
- LLM을 활용한 논문 요약
- 구조화된 프롬프트 생성
- 한국어 요약 지원

### Presenter Agent
- Jinja2 템플릿 기반 리포트 생성
- 이미지 Base64 인코딩 및 임베딩
- 반응형 HTML 디자인

## 🛠️ 개발 및 확장

### 새로운 카테고리 추가

`config/config.yaml`에서 `category` 값을 변경:

```yaml
arxiv:
  category: "cs.AI"  # 인공지능
  # category: "cs.CV"  # 컴퓨터 비전
  # category: "cs.CL"  # 자연어 처리
```

### 템플릿 커스터마이징

`templates/summary_report.html`을 수정하여 리포트 디자인 변경 가능

### 로깅 설정

```yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
  file: "arxiv_summarizer.log"
```

## 📊 Agent Lightning 통합 (향후 계획)

이 프로젝트는 향후 [Agent Lightning](https://github.com/microsoft/agent-lightning)과 통합하여:

- 강화학습을 통한 요약 품질 개선
- 자동 프롬프트 최적화
- 성능 추적 및 분석

을 지원할 예정입니다.

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 🙏 감사의 글

- [arXiv](https://arxiv.org/) - 오픈 액세스 논문 저장소
- [SKT-AI](https://github.com/SKT-AI/A.X-4.0) - A.X-4.0 LLM API 제공
- [Agent Lightning](https://github.com/microsoft/agent-lightning) - AI 에이전트 최적화 프레임워크

## 📞 문의

이슈나 질문은 GitHub Issues를 통해 남겨주세요.
