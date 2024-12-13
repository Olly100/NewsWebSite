# main_script.py
import logging
from logging_config import setup_logging
from ingestion.fetch_rss import fetch_rss
from parsing.parse_data import parse_feed, store_parsed_articles
import asyncio
import os
from db.database import get_rss_sources, setup_database
from enrichment.llm_enrichment import AnthropicEnricher, enrich_articles
from dotenv import load_dotenv
import subprocess
import sys
import atexit

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = setup_logging()

def run_flask_app():
    # Start the Flask app as a subprocess
    process = subprocess.Popen([sys.executable, 'frontend/app.py'])
    return process

async def main():
    logger.info("########################## Starting the main function... ##########################")
    try:
        # Setup database if needed
        setup_database()
        

        # Fetch RSS sources from the database
        rss_sources = get_rss_sources()
        if not rss_sources:
            logger.error("No active RSS sources found.")
            return

        # Initialize the enricher
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            return
            
        enricher = AnthropicEnricher(api_key)

        # Fetch RSS data
        entries = await fetch_rss(rss_sources)
        if entries:
            # Group entries by source
            source_entries = {source: [] for source in rss_sources}
            for entry in entries:
                source_entries[entry["rss_feed"]].append(entry)

            # Process each source's entries
            for source, entries in source_entries.items():
                # Parse the feed
                articles = parse_feed(entries, source, limit=2)
                logger.info(f"Parsed {len(articles)} articles from {source}.")
                
                # Enrich articles with keywords
                enriched_articles = await enrich_articles(articles, enricher)
                logger.info(f"Enriched {len(enriched_articles)} articles from {source}.")
                
                # Store the enriched articles
                await store_parsed_articles(enriched_articles)
                logger.info(f"Stored enriched articles from {source} in the database.")
                
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    flask_process = run_flask_app()
    atexit.register(flask_process.terminate)  # Ensure the Flask app is terminated on exit
    print("Flask app is running...")
    asyncio.run(main())
