#!/usr/bin/env python3
"""
arXiv Paper Summarizer - Main Entry Point

This script fetches recent papers from arXiv, summarizes them using LLM,
and generates an HTML report with images.
"""

import logging
import sys
from pathlib import Path

from utils.config_loader import ConfigLoader
from utils.agent_lightning_tracker import AgentLightningTracker
from utils.novelty_ranker import NoveltyRanker
from agents.fetcher import FetcherAgent
from agents.summarizer import SummarizerAgent
from agents.presenter import PresenterAgent


def setup_logging(config: ConfigLoader) -> None:
    """
    Set up logging configuration.

    Args:
        config: Configuration loader instance
    """
    log_level = config.get('logging.level', 'INFO')
    log_file = config.get('logging.file', 'arxiv_summarizer.log')

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    if log_path.parent != Path('.'):
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main execution function."""
    print("=" * 60)
    print("arXiv Paper Summarizer")
    print("=" * 60)
    print()

    # Load configuration
    print("📋 Loading configuration...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.config
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        sys.exit(1)

    # Set up logging
    setup_logging(config_loader)
    logger = logging.getLogger(__name__)

    logger.info("Starting arXiv Paper Summarizer")

    try:
        # Initialize Agent Lightning tracker
        tracker = AgentLightningTracker(config)
        if tracker.enabled:
            print("\n⚡ Agent Lightning tracking enabled")

        # Initialize agents
        print("\n🤖 Initializing agents...")
        fetcher = FetcherAgent(config)
        summarizer = SummarizerAgent(config, tracker=tracker)
        presenter = PresenterAgent(config)
        print("✅ All agents initialized")

        # Step 1: Fetch metadata only (no PDF download yet)
        print("\n📥 Fetching paper metadata from arXiv...")
        category = config.get('arxiv', {}).get('category', 'eess.AS')
        max_results = config.get('arxiv', {}).get('max_results', 10)
        print(f"   Category: {category}")
        print(f"   Max results: {max_results}")

        metadata_list = fetcher.fetch_metadata_only()

        if not metadata_list:
            print("⚠️  No papers fetched. Exiting.")
            logger.warning("No papers were fetched")
            return

        print(f"✅ Successfully fetched metadata for {len(metadata_list)} papers")

        # Step 1.5: Filter papers by novelty (if enabled)
        novelty_config = config.get('novelty_filter', {})
        if novelty_config.get('enabled', False):
            print("\n🎯 Filtering papers by novelty and importance...")
            top_papers_count = novelty_config.get('top_papers_count', 10)
            print(f"   Analyzing {len(metadata_list)} abstracts")
            print(f"   Selecting top {top_papers_count} papers")

            ranker = NoveltyRanker(config)
            filtered_metadata = ranker.rank_papers(metadata_list)

            print(f"✅ Selected {len(filtered_metadata)} papers based on novelty ranking")
            papers_to_process = filtered_metadata
        else:
            print("\n⏭️  Novelty filtering disabled, processing all papers")
            papers_to_process = metadata_list

        # Step 2: Download and process selected papers
        print(f"\n📦 Downloading and processing {len(papers_to_process)} papers...")
        paper_data_list = []
        for i, paper_metadata in enumerate(papers_to_process):
            try:
                print(f"   [{i+1}/{len(papers_to_process)}] Processing {paper_metadata['metadata']['arxiv_id']}...")
                paper_data = fetcher.process_paper(paper_metadata)
                paper_data_list.append(paper_data)
            except Exception as e:
                logger.error(f"Failed to process paper: {e}")
                continue

        if not paper_data_list:
            print("⚠️  No papers were successfully processed. Exiting.")
            logger.warning("No papers were successfully processed")
            return

        print(f"✅ Successfully processed {len(paper_data_list)} papers")

        papers_to_summarize = paper_data_list

        # Step 3: Summarize papers
        print("\n📝 Creating summaries with LLM...")
        summaries = summarizer.summarize_papers(papers_to_summarize)
        print(f"✅ Created {len(summaries)} summaries")

        # Step 4: Generate report
        print("\n📊 Generating HTML report...")
        report_path = presenter.create_report(summaries)
        print(f"✅ Report generated: {report_path}")

        # Save Agent Lightning session
        if tracker.enabled:
            tracker.save_session()
            summary = tracker.get_summary()
            print(f"\n⚡ Agent Lightning session saved:")
            print(f"   Events tracked: {summary['total_events']}")
            print(f"   Store path: {summary['store_path']}")

        # Summary
        print("\n" + "=" * 60)
        print("✨ Process completed successfully!")
        print("=" * 60)
        print(f"\n📄 Summary Report: {report_path}")
        print(f"📚 Papers processed: {len(paper_data_list)}")
        print(f"📁 Data directory: data/")
        print()

        logger.info("arXiv Paper Summarizer completed successfully")

    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        logger.warning("Process interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        logger.error(f"Error during execution: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
