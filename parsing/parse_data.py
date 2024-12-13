"""
Module: parse_data.py
Purpose: Extract and normalize fields (e.g., title, description, source).
"""
import sqlite3
import ast  # For safely evaluating serialized Python dictionaries
import logging
from datetime import datetime
import json  # Import the json module
from db.database import initialize_database  # Import from centralized db module
from enrichment.llm_enrichment import AnthropicEnricher, enrich_articles
import os
import asyncio

# Logger initialization
logger = logging.getLogger(__name__)

def get_existing_articles(db_name="news_ingestion.db"):
    """Get existing article titles and sources from database"""
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT title, source FROM parsed_articles')
            return {(title, source) for title, source in cursor.fetchall()}
    except Exception as e:
        logger.error(f"Error getting existing articles: {e}")
        return set()

def parse_feed(entries, rss_feed, limit=2, db_name="news_ingestion.db"):
    logger.info(f"Parsing feed entries (limit: {limit})...")
    
    if not isinstance(entries, list) or not entries:
        logger.error("No valid entries to parse.")
        return []

    # Get existing articles
    existing_articles = get_existing_articles(db_name)
    
    # Filter out invalid entries and normalize fields
    articles = []
    for entry in entries[:limit]:
        if not entry.get("title") or not entry.get("link"):
            continue
            
        title = entry.get("title", "Untitled")
        # Check if article already exists
        if (title, rss_feed) in existing_articles:
            logger.info(f"Skipping existing article")
            continue
            
        articles.append({
            "title": title,
            "description": entry.get("summary") or entry.get("description", "No description available."),
            "link": entry.get("link"),
            "source": rss_feed,
            "published_date": (
                entry.get("pubDate") or entry.get("published", "Unknown Date")
            ),
            "parsed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # Format the published_date correctly for new articles
    for article in articles:
        if article["published_date"] != "Unknown Date":
            try:
                # Check if the date string contains 'GMT'
                if 'GMT' in article["published_date"]:
                    article["published_date"] = datetime.strptime(article["published_date"], 
                                                                "%a, %d %b %Y %H:%M:%S %Z").strftime("%d %b %Y %H:%M")
                # Handle ISO format dates (e.g., 2024-12-12T23:05:14-05:00)
                elif 'T' in article["published_date"]:
                    iso_date = datetime.fromisoformat(article["published_date"])
                    article["published_date"] = iso_date.strftime("%d %b %Y %H:%M")
                else:
                    # Handle the +0000 format
                    article["published_date"] = datetime.strptime(article["published_date"], 
                                                                "%a, %d %b %Y %H:%M:%S %z").strftime("%d %b %Y %H:%M")
            except ValueError as e:
                logger.error(f"Error parsing date: {e}")
                article["published_date"] = "Unknown Date"

    logger.info(f"Successfully parsed {len(articles)} new articles.")
    return articles

async def store_parsed_articles(articles, db_name="news_ingestion.db"):
    """Store parsed articles in the database."""
    if not articles:
        logger.warning("No articles to store.")
        return

    try:
        with sqlite3.connect(db_name) as connection:
            cursor = connection.cursor()

            for article in articles:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO parsed_articles 
                        (title, description, source, link, published_date, parsed_at, 
                         keywords, importance, derived_summary)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        article.get("title"), 
                        article.get("description"), 
                        article.get("source"), 
                        article.get("link"),
                        article.get("published_date"), 
                        article.get("parsed_at", None),
                        article.get("keywords", "uncategorized"),
                        article.get("importance", "low"),
                        article.get("derived_summary")
                    ))
                    
                except Exception as e:
                    logger.error(f"Error storing article {article.get('title')}: {e}")

            connection.commit()
            logger.info(f"Stored {len(articles)} articles.")
            
    except Exception as e:
        logger.error(f"Error in store_parsed_articles: {e}")
        logger.exception("Full traceback:")