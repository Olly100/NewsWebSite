# main_script.py
import asyncio
import sys
import os
from hypercorn.asyncio import serve
from hypercorn.config import Config as HypercornConfig
import logging
from dotenv import load_dotenv


# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your modules after modifying the path
from db.database import setup_database, get_rss_sources
from ingestion.fetch_rss import fetch_rss
from parsing.parse_data import parse_feed, store_parsed_articles
from enrichment.llm_enrichment import AnthropicEnricher, enrich_articles
import frontend.app as app_module  # Ensure this import is present
from pipeline.rss_manager import refresh_rss_feeds  # Import the refresh function from rss_manager

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

async def run_flask_app():
    config = HypercornConfig()
    config.bind = ["127.0.0.1:5000"]  # Adjust as needed
    app = app_module.create_app()  # Ensure app_module is defined
    await serve(app, config)

async def main():
    logger.info("########################## Starting the main function... ##########################")
    try:
        # Setup database if needed
        setup_database()

        # Initialize the enricher
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            return
            
        enricher = AnthropicEnricher(api_key)

        # Call the refresh_rss_feeds function from rss_manager
        result_message = await refresh_rss_feeds(enricher)
        logger.info(result_message)

    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    async def combined_tasks():
        await asyncio.gather(run_flask_app(), main())

    asyncio.run(combined_tasks())