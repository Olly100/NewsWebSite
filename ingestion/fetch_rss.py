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
        if response.status != 200:
            logger.error(f"Failed to fetch {feed_url}: {response.status}")
            raise Exception(f"HTTP error: {response.status}")
        return await response.text()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def fetch_rss(rss_sources):
    try:
        fetched_data = []

        async with aiohttp.ClientSession() as session:
            tasks = [fetch_feed(session, url) for url in rss_sources]
            responses = await asyncio.gather(*tasks)

        for response, source_url in zip(responses, rss_sources):
            feed = feedparser.parse(response)
            if feed.bozo:
                logger.warning(f"Parsing error in RSS feed: {feed.bozo_exception}")
                continue

            if not feed.entries:
                logger.warning(f"No entries found in feed: {source_url}")
                continue

            for entry in feed.entries:
                entry["rss_feed"] = source_url  # Ensure the correct source is assigned to each entry

            fetched_data.extend(feed.entries)  # Add entries directly to the main list

        logger.info("Successfully fetched data from the RSS feed.")
        return fetched_data
    except Exception as e:
        logger.error(f"An error occurred while fetching the RSS feed: {e}")
        return None
