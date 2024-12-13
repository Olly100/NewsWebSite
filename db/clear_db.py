import sqlite3
import logging

logger = logging.getLogger(__name__)

def drop_tables(db_name="news_ingestion.db"):
    """
    Drop all tables from the database to allow complete rebuild
    """
    try:
        with sqlite3.connect(db_name) as connection:
            cursor = connection.cursor()
            
            # Get list of all tables, excluding SQLite system tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                AND name NOT LIKE 'sqlite_%'
            """)
            tables = cursor.fetchall()
            
            # Drop each table
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                logger.info(f"Dropped table: {table_name}")
            
            connection.commit()
            logger.info("All tables dropped successfully")
            
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    drop_tables() 