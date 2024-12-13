import sqlite3
import logging
import os
from db.populate_rss_sources import populate_rss_sources

logger = logging.getLogger(__name__)

def check_database_exists(db_name="news_ingestion.db"):
    """Check if database exists and has required tables"""
    if not os.path.exists(db_name):
        return False
    
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT count(name) FROM sqlite_master 
                WHERE type='table' 
                AND name IN ('rss_sources', 'raw_feed', 'parsed_articles', 'app_config')
            """)
            count = cursor.fetchone()[0]
            return count == 4  # All four tables exist
    except Exception as e:
        logger.error(f"Error checking database: {e}")
        return False

def setup_database(db_name="news_ingestion.db"):
    """Initialize database and populate if needed"""
    if not check_database_exists(db_name):
        logger.info("Database not found or incomplete. Initializing...")
        initialize_database(db_name)
        logger.info("Populating RSS sources...")
        populate_rss_sources(db_name)
        return True
    return False

def initialize_database(db_name="news_ingestion.db"):
    # Connect to SQLite database
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Add config table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,  -- 'text', 'number', 'select', etc.
            options TEXT,        -- JSON array for select options
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default configurations if they don't exist
    default_configs = [
        ('log_level', 'INFO', 'Logging level', 'select', '["DEBUG", "INFO", "WARNING", "ERROR"]'),
        ('llm_provider', 'anthropic', 'LLM Provider', 'select', '["anthropic", "openai"]'),
        ('summary_max_words', '100', 'Maximum words in article summary', 'number', None),
        ('article_fetch_limit', '2', 'Number of articles to fetch per source', 'number', None),
        ('fetch_interval_minutes', '30', 'RSS fetch interval in minutes', 'number', None),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO app_config (key, value, description, type, options)
        VALUES (?, ?, ?, ?, ?)
    ''', default_configs)

    # Create rss_sources table with feed_type
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rss_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_url TEXT NOT NULL UNIQUE,
            source_name TEXT NOT NULL,
            category TEXT,
            feed_type TEXT DEFAULT 'RSS',
            last_fetched TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Create raw_feed table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_feed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_url TEXT NOT NULL,
            fetched_data TEXT NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create parsed_articles table with UNIQUE constraint and link column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parsed_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            source TEXT NOT NULL,
            link TEXT,
            published_date TIMESTAMP,
            parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            derived_summary TEXT,
            keywords TEXT,
            importance TEXT,
            UNIQUE(title, source)
        )
    ''')

    # Commit and close
    connection.commit()
    connection.close()
    logger.info(f"Database '{db_name}' initialized successfully!")

def get_rss_sources(db_name="news_ingestion.db"):
    with sqlite3.connect(db_name) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT feed_url FROM rss_sources WHERE status = 'active'")
        sources = cursor.fetchall()
        return [source[0] for source in sources]

if __name__ == "__main__":
    initialize_database()
