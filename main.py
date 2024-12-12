# main_script.py
import logging
from logging_config import setup_logging
from ingestion.fetch_rss import fetch_rss
from parsing.parse_data import parse_feed, store_parsed_articles
import asyncio  # Import asyncio for running async functions
import os
from db.database import get_rss_sources  # Import the function to get RSS sources

# Set up logging
logger = setup_logging()

async def main():
    logger.info("Starting the main function...")
    try:
        # Fetch RSS sources from the database
        rss_sources = get_rss_sources()  # Get the active RSS feed sources

        if not rss_sources:
            logger.error("No active RSS sources found.")
            return

        # Fetch RSS data
        entries = await fetch_rss(rss_sources)  # Pass the sources to fetch_rss
        if entries:
            # Group entries by source
            source_entries = {source: [] for source in rss_sources}
            for entry in entries:
                source_entries[entry["rss_feed"]].append(entry)

            # Process each source's entries
            for source, entries in source_entries.items():
                articles = parse_feed(entries, source)  # Pass the entries and the source URL
                logger.info(f"Parsed {len(articles)} articles from {source}.")
                
                store_parsed_articles(articles)
                logger.info(f"Stored parsed articles from {source} in the database.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    
    asyncio.run(main())  # Run the main function using asyncio
