"""Paper fetcher agents."""

from .arxiv import ArxivFetcher
from .huggingface import HuggingFaceFetcher

__all__ = [
    "ArxivFetcher",
    "HuggingFaceFetcher",
]
