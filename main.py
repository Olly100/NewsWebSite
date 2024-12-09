# main_script.py
import logging
from logging_config import setup_logging
from ingestion.fetch_rss import fetch_rss
from parsing.parse_data import parse_feed
from tenacity import retry, stop_after_attempt, wait_exponential


logger = setup_logging()

# Configure logging (if not done in another module)
logging.basicConfig(level=logging.INFO)

@retry(
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff
    reraise=True  # Re-raise exception after retries fail
)
def fetch_and_parse_rss():
    """
    Fetch and parse the RSS feed in a single pipeline.
    :return: List of parsed articles or None if an error occurs.
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting to fetch and parse RSS feed.")

    # Step 1: Fetch the RSS feed
    feed = fetch_rss()
    if not feed:
        logger.error("Failed to fetch RSS feed. Exiting pipeline.")
        return None

    # Step 2: Parse the fetched feed
    articles = parse_feed(feed)
    if not articles:
        logger.error("No articles could be parsed from the feed.")
        return None

    logger.info(f"Pipeline completed successfully with {len(articles)} articles parsed.")
    print(articles)
    return articles



if __name__ == "__main__":
    fetch_and_parse_rss()