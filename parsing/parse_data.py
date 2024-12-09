"""
Module:parse_data.py
Purpose: Extract and normalize fields (e.g., title, description, source).
"""

from datetime import datetime
import logging

def validate_article(article):
    # Example validation: Check if title and link are present
    if not article.get("title") or not article.get("link"):
        return False
    return True

def parse_feed(feed):
    logger = logging.getLogger(__name__)
    articles = []

    if not feed or not hasattr(feed, 'entries'):
        logger.error("Feed is invalid or does not contain entries.")
        return None

    for entry in feed.entries:
        try:
            article = {
                "title": getattr(entry, 'title', "Untitled"),
                "description": getattr(entry, 'description', "No description available."),
                "published": getattr(entry, 'published', "Unknown date"),
                "link": getattr(entry, 'link', None)
            }

            if not validate_article(article):
                logger.warning(f"Skipping invalid article: {article}")
                continue

            articles.append(article)
        except Exception as e:
            logger.warning(f"Error while parsing entry: {e}")
            continue

    logger.info(f"Successfully parsed {len(articles)} articles.")
    return articles
