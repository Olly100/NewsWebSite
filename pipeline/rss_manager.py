import asyncio
import logging
from ingestion.fetch_rss import fetch_rss
from parsing.parse_data import parse_feed, store_parsed_articles
from enrichment.llm_enrichment import enrich_articles, AnthropicEnricher
from db.database import get_rss_sources

# Set up logging
logger = logging.getLogger(__name__)

async def refresh_rss_feeds(enricher):
    """Fetch, parse, enrich, and store RSS feeds."""
    logger.info("Starting the RSS feed refresh process.")
    try:
        # Fetch RSS sources from the database
        rss_sources = get_rss_sources()
        if not rss_sources:
            logger.warning("No active RSS sources found.")
            return "No active RSS sources found."

        # Fetch RSS data
        logger.info("Fetching RSS data from sources.")
        entries = await fetch_rss(rss_sources)
        if entries:
            logger.info(f"Fetched {len(entries)} entries from RSS sources.")

            # Group entries by source
            source_entries = {source: [] for source in rss_sources}
            for entry in entries:
                source_entries[entry["rss_feed"]].append(entry)

            # Process each source's entries
            for source, entries in source_entries.items():
                logger.info(f"Processing entries for source: {source}")
                articles = parse_feed(entries, source, limit=2)
                enriched_articles = await enrich_articles(articles, enricher)
                await store_parsed_articles(enriched_articles)

            return "Feeds refreshed and new stories ingested successfully."
        else:
            logger.info("No new entries found in the RSS feeds.")
            return "No new entries found in the RSS feeds."
    except Exception as e:
        logger.error(f"Error refreshing feeds: {str(e)}")
        return f"Error refreshing feeds: {str(e)}" 