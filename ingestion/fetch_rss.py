"""
Module: ingestion.fetch_rss
Purpose: Functions to fetch RSS data from external sources.
"""
import logging
import feedparser
import requests
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential

# Logger initialization
logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff
    reraise=True  # Re-raise exception after retries
)
def fetch_rss():
    from config import RSS_FEED_URL  # Ensure this import is local if config isn't global

    logger.info(f"Fetching RSS feed from: {RSS_FEED_URL}")
    
    try:
        # Fetch the RSS feed data
        response = requests.get(RSS_FEED_URL, timeout=10)
        response.raise_for_status()  # Raise error for HTTP issues

        # Parse the RSS feed
        feed = feedparser.parse(response.text)

        # Check for parsing errors
        if feed.bozo:
            logger.warning(f"Parsing error in RSS feed: {feed.bozo_exception}")
            return None

        if not feed.entries:
            logger.warning("No entries found in the feed.")
            return None

        logger.info(f"Successfully fetched RSS feed with {len(feed.entries)} entries.")
        return feed

    except RequestException as e:
        logger.error(f"Network error occurred while fetching RSS feed from {RSS_FEED_URL}: {e}")
        return None

    except Exception as e:
        logger.critical(f"An unexpected error occurred while fetching RSS feed from {RSS_FEED_URL}: {e}", exc_info=True)
        return None
