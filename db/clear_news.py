import sqlite3
import logging

# Set up logging
logger = logging.getLogger(__name__)

def clear_database(db_name="news_ingestion.db"):
    """Clear all data from the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # List of tables to clear
    tables = ["parsed_articles", "raw_feed"]

    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            conn.commit()
            print(f"Cleared data from table: {table}")
        except sqlite3.OperationalError as e:
            print(f"Error clearing table {table}: {e}")

    conn.close()
    logger.info(f"Database '{db_name}' has been cleared.")  # New log entry for the entire database clear

if __name__ == "__main__":
    clear_database()
