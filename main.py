# main_script.py
import logging
from logging_config import setup_logging
from ingestion.fetch_rss import fetch_rss
from parsing.parse_data import parse_feed, store_parsed_articles
import asyncio  # Import asyncio for running async functions
import os

# Set up logging
logger = setup_logging()

async def main():
    logger.info("Starting the main function...")
    try:
        fetched_data = await fetch_rss()
        logger.info("Fetched data from RSS feed.")
        
        articles = parse_feed(fetched_data)
        logger.info(f"Parsed {len(articles)} articles.")
        
        store_parsed_articles(articles)
        logger.info("Stored parsed articles in the database.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    
    asyncio.run(main())  # Run the main function using asyncio
