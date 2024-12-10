# main_script.py
import logging
from logging_config import setup_logging
from ingestion.fetch_rss import fetch_rss
from parsing.parse_data import parse_feed, store_parsed_articles
import asyncio  # Import asyncio for running async functions

# Set up logging
logger = setup_logging()

async def main():
    # Fetch RSS feeds and store raw data
    fetched_data = await fetch_rss()  # Await the asynchronous fetch_rss
    
    # Parse the fetched data
    articles = parse_feed(fetched_data)
    
    # Store parsed articles in the database
    store_parsed_articles(articles)

if __name__ == "__main__":
    asyncio.run(main())  # Run the main function using asyncio