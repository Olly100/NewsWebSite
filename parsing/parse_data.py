"""
Module:parse_data.py
Purpose: Extract and normalize fields (e.g., title, description, source).
"""
import sqlite3
import ast  # For safely evaluating serialized Python dictionaries
import logging
from datetime import datetime
import json  # Import the json module

# Logger initialization
logger = logging.getLogger(__name__)

def parse_serialized_feed(fetched_data):
    """
    Deserialize the fetched data and parse it into articles.

    :param fetched_data: The JSON string containing the fetched feed data.
    :return: List of parsed articles.
    """
    logger.info("Deserializing fetched data...")
    
    try:
        # Deserialize JSON feed data
        feed = json.loads(fetched_data)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return []

    articles = []

    # Check if the feed has entries
    if not feed or not hasattr(feed, 'entries'):
        logger.error("Feed is invalid or does not contain entries.")
        return []

    for entry in feed['entries']:
        try:
            article = {
                "title": entry.get("title", "No Title"),
                "description": entry.get("description", "No Description"),
                "link": entry.get("link", None),
                "published": entry.get("published", "Unknown Date")
            }
            articles.append(article)
        except Exception as e:
            logger.warning(f"Error while parsing entry: {e}")
            continue

    logger.info(f"Successfully parsed {len(articles)} articles.")
    return articles

def parse_feed(entries):
    logger.info("Parsing feed entries...")
    
    if not isinstance(entries, list) or not entries:
        logger.error("No valid entries to parse.")
        return []

    # Filter out invalid entries
    articles = [
        {
            "title": entry.get("title", "Untitled"),
            "description": entry.get("summary", "No description available."),
            "link": entry.get("link"),
            "published": entry.get("published", "Unknown date"),
        }
        for entry in entries
        if entry.get("title") and entry.get("link")  # Only include entries with both title and link
    ]

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

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Prepare a list of tuples for batch insertion
    article_tuples = [
        (article['title'], article['description'], article['link'], article['published'], datetime.now().isoformat())
        for article in articles
    ]

    cursor.executemany('''
        INSERT INTO parsed_articles (title, description, source, published_date, parsed_at)
        VALUES (?, ?, ?, ?, ?)
    ''', article_tuples)

    connection.commit()
    connection.close()
    logger.info(f"Stored {len(articles)} articles.")

def parse_and_store_articles(db_name="news_ingestion.db"):
    """
    Fetch raw feed data from the database, parse it, and store normalized articles.

    :param db_name: Name of the SQLite database file.
    """
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    try:
        # Step 1: Fetch raw feed data
        cursor.execute("SELECT fetched_data FROM raw_feed")
        raw_feeds = cursor.fetchall()

        if not raw_feeds:
            logger.warning("No raw feeds available to parse.")
            return

        for (fetched_data,) in raw_feeds:  # Unpack the tuple
            logger.info("Parsing raw feed data...")
            try:
                # Deserialize JSON feed data
                feed = json.loads(fetched_data)
                articles = parse_feed(feed['entries'])  # Pass the entries directly

                # Step 2: Store parsed articles in the parsed_articles table
                store_parsed_articles(articles, connection)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON: {e}")
            except Exception as e:
                logger.warning(f"Error while processing raw feed data: {e}")

    finally:
        connection.close()
        logger.info("Parsing and storing articles complete.")
