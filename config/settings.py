from decouple import config
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # Example configurations
    DB_URL = config('DB_URL', default='sqlite:///default.db')  # Default to a SQLite database
    LOG_LEVEL = config('LOG_LEVEL', default='INFO')  # Default log level
    RSS_FEED_URL = config('RSS_FEED_URL', default='https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml')  # Example RSS feed URL
    DB_NAME = os.getenv("DB_NAME", "news_ingestion.db")  # Default if not set
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")