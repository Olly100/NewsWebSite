import logging
import feedparser
import requests
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential
import sqlite3
from datetime import datetime
import json  # Import the json module
import aiohttp
import asyncio

# Logger initialization
logger = logging.getLogger(__name__)

async def fetch_feed(session, feed_url):
    async with session.get(feed_url) as response:
        return await response.text()

@retry(
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff
    reraise=True  # Re-raise exception after retries fail
)
async def fetch_rss():
    rss_sources = [
        'https://www.prnewswire.co.uk/rss/news-releases-list.rss',
        'https://feeds.bbci.co.uk/news/rss.xml',
        'https://www.theverge.com/rss/index.xml'
    ]

    fetched_data = []  # Initialize a list to hold all fetched entries

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, url) for url in rss_sources]
        responses = await asyncio.gather(*tasks)

    for response in responses:
        feed = feedparser.parse(response)
        if feed.bozo:
            logger.warning(f"Parsing error in RSS feed: {feed.bozo_exception}")
            continue

        if not feed.entries:
            logger.warning(f"No entries found in feed: {feed_url}")
            continue

        fetched_data.extend(feed.entries)  # Add entries directly to the main list

    logger.debug(f"Fetched data structure: {fetched_data}")  # Log the fetched data structure
    return fetched_data  # Return the flattened list of entries
