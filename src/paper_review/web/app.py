"""FastAPI web application."""

from datetime import date, timedelta
from pathlib import Path
from typing import List

from fastapi import BackgroundTasks, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from paper_review.core.config import ConfigLoader
from paper_review.core.pipeline import PaperReviewPipeline
from paper_review.models import FilterConfig, SummaryReport

# Initialize FastAPI app
app = FastAPI(
    title="Paper Review Service",
    description="AI/ML 논문 자동 수집 및 요약 서비스",
    version="0.2.0",
)

# Setup templates and static files
BASE_DIR = Path(__file__).parent.parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates" / "web"))

# Mount static files if directory exists
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Load configuration
config_loader = ConfigLoader()
config = config_loader.config

# Global state for storing latest report
latest_report: SummaryReport | None = None
is_running: bool = False


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """홈 페이지 - 필터 설정 폼."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "latest_report": latest_report,
            "is_running": is_running,
        },
    )


@app.get("/papers", response_class=HTMLResponse)
async def list_papers(
    request: Request,
    sources: str = "arxiv,huggingface",
    arxiv_categories: str = "",
    arxiv_filter_mode: str = "OR",
    hf_keywords: str = "",
    hf_filter_mode: str = "OR",
    days_back: int = 1,
):
    """
    논문 리스트 페이지 (SSR).

    Query parameters:
        sources: 논문 소스 (comma-separated)
        arxiv_categories: arXiv 카테고리 (comma-separated)
        arxiv_filter_mode: AND 또는 OR
        hf_keywords: HF 키워드 (comma-separated)
        hf_filter_mode: AND 또는 OR
        days_back: 최근 N일
    """
    # Parse sources
    source_list = [s.strip() for s in sources.split(",") if s.strip()]

    # Parse categories and keywords
    categories = [c.strip() for c in arxiv_categories.split(",") if c.strip()]
    keywords = [k.strip() for k in hf_keywords.split(",") if k.strip()]

    # Create filter config
    filter_config = FilterConfig(
        sources=source_list,
        days_back=days_back,
        arxiv_categories=categories,
        arxiv_filter_mode=arxiv_filter_mode,
        hf_keywords=keywords,
        hf_filter_mode=hf_filter_mode,
    )

    # Run pipeline
    pipeline = PaperReviewPipeline(config)
    report = await pipeline.run(filter_config, process_pdfs=False)

    global latest_report
    latest_report = report

    return templates.TemplateResponse(
        "papers.html",
        {
            "request": request,
            "report": report,
            "filter_config": filter_config,
        },
    )


@app.post("/api/fetch")
async def fetch_papers(
    background_tasks: BackgroundTasks,
    sources: str = Form(...),
    arxiv_categories: str = Form(""),
    arxiv_filter_mode: str = Form("OR"),
    hf_keywords: str = Form(""),
    hf_filter_mode: str = Form("OR"),
    days_back: int = Form(1),
):
    """
    논문 수집 시작 (백그라운드).

    Form data:
        sources: 논문 소스 (comma-separated)
        arxiv_categories: arXiv 카테고리
        arxiv_filter_mode: AND 또는 OR
        hf_keywords: HF 키워드
        hf_filter_mode: AND 또는 OR
        days_back: 최근 N일
    """
    # Parse sources
    source_list = [s.strip() for s in sources.split(",") if s.strip()]

    # Parse categories and keywords
    categories = [c.strip() for c in arxiv_categories.split(",") if c.strip()]
    keywords = [k.strip() for k in hf_keywords.split(",") if k.strip()]

    # Create filter config
    filter_config = FilterConfig(
        sources=source_list,
        days_back=days_back,
        arxiv_categories=categories,
        arxiv_filter_mode=arxiv_filter_mode,
        hf_keywords=keywords,
        hf_filter_mode=hf_filter_mode,
    )

    # Add task to background
    background_tasks.add_task(run_pipeline_background, filter_config)

    global is_running
    is_running = True

    return {"status": "started", "message": "논문 수집을 시작했습니다"}


async def run_pipeline_background(filter_config: FilterConfig):
    """백그라운드에서 파이프라인 실행."""
    global latest_report, is_running

    try:
        logger.info("Starting background pipeline")
        pipeline = PaperReviewPipeline(config)
        report = await pipeline.run(filter_config, process_pdfs=True)
        latest_report = report
        logger.info(f"Background pipeline completed: {report.total_papers} papers")
    except Exception as e:
        logger.error(f"Background pipeline failed: {e}")
    finally:
        is_running = False


@app.get("/api/status")
async def get_status():
    """진행 상황 확인."""
    return {
        "is_running": is_running,
        "latest_report": latest_report.model_dump() if latest_report else None,
    }


@app.get("/api/papers")
async def get_papers_json():
    """논문 리스트 JSON으로 반환."""
    if latest_report:
        return latest_report.model_dump()
    return {"total_papers": 0, "summaries": []}


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행."""
    logger.info("Paper Review Service started")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행."""
    logger.info("Paper Review Service stopped")
