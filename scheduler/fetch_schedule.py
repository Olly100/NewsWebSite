"""
Module: fetch_schedule.py
Purpose: Scheduled RSS fetching that runs independently of the web app
"""
import asyncio
import schedule
import time
import sys
import os
import logging
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from main import main as fetch_main
from logging_config import setup_logging

logger = setup_logging()

async def scheduled_fetch():
    """Run the RSS fetch process"""
    try:
        logger.info(f"Starting scheduled fetch at {datetime.now()}")
        await fetch_main()
        logger.info("Completed scheduled fetch")
    except Exception as e:
        logger.error(f"Error in scheduled fetch: {e}")

def run_schedule():
    """Run the scheduler"""
    schedule.every(30).minutes.do(lambda: asyncio.run(scheduled_fetch()))
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    logger.info("Starting RSS fetch scheduler")
    # Run initial fetch
    asyncio.run(scheduled_fetch())
    # Start scheduler
    run_schedule() 