"""
Module: parse_data.py
Purpose: Extract and normalize fields (e.g., title, description, source).
"""
import sqlite3
import ast  # For safely evaluating serialized Python dictionaries
import logging
from datetime import datetime
import json  # Import the json module

# Logger initialization
logger = logging.getLogger(__name__)

def parse_feed(entries, rss_feed):
    logger.info("Parsing feed entries...")
    
    if not isinstance(entries, list) or not entries:
        logger.error("No valid entries to parse.")
        return []

    # Filter out invalid entries and normalize fields
    articles = [
        {
            "title": entry.get("title", "Untitled"),
            "description": entry.get("summary") or entry.get("description", "No description available."),
            "link": entry.get("link"),
            "source": rss_feed,  # Use the rss_feed passed to the function
            "published_date": (
                # Get the date string from pubDate or published
                entry.get("pubDate") or entry.get("published", "Unknown Date")
            ),
            "parsed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Add parsed timestamp
        }
        for entry in entries
        if entry.get("title") and entry.get("link")  # Only include entries with both title and link
    ]

    # Format the published_date correctly
    for article in articles:
        if article["published_date"] != "Unknown Date":
            try:
                # Check if the date string contains 'GMT'
                if 'GMT' in article["published_date"]:
                    article["published_date"] = datetime.strptime(article["published_date"], 
                                                                  "%a, %d %b %Y %H:%M:%S %Z").strftime("%d %b %Y %H:%M")
                else:
                    # Handle the +0000 format
                    article["published_date"] = datetime.strptime(article["published_date"], 
                                                                  "%a, %d %b %Y %H:%M:%S %z").strftime("%d %b %Y %H:%M")
            except ValueError as e:
                logger.error(f"Error parsing date: {e}")
                article["published_date"] = "Unknown Date"

    logger.info(f"Successfully parsed {len(articles)} articles.")
    return articles

def store_parsed_articles(articles, db_name="news_ingestion.db"):
    """
    Store parsed articles in the database.

    :param articles: List of articles to store.
    :param db_name: Name of the SQLite database file.
    """
    if not articles:
        logger.warning("No articles to store.")
        return

    with sqlite3.connect(db_name) as connection:
        cursor = connection.cursor()

        # Use INSERT OR REPLACE to avoid duplicates
        cursor.executemany('''
            INSERT OR REPLACE INTO parsed_articles (title, description, source, link, published_date, parsed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [
            (
                article.get("title"), 
                article.get("description"), 
                article.get("source"), 
                article.get("link"),  # Handle missing fields gracefully
                article.get("published_date"), 
                article.get("parsed_at", None)  # Default to None if not provided
            ) for article in articles
        ])

        connection.commit()

    logger.info(f"Stored {len(articles)} articles.")

def initialize_database(db_name):
    with sqlite3.connect(db_name) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parsed_articles (
                title TEXT,
                description TEXT,
                source TEXT,
                link TEXT,  -- Ensure this line is present
                published_date TEXT,
                parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        connection.commit()