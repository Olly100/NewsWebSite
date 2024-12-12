import sqlite3

def initialize_database(db_name="news_ingestion.db"):
    # Connect to SQLite database
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

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
            UNIQUE(title, source) -- Enforce uniqueness on title and source
        )
    ''')

    # Commit and close
    connection.commit()
    connection.close()
    print(f"Database '{db_name}' initialized successfully!")

def get_rss_sources(db_name="news_ingestion.db"):
    with sqlite3.connect(db_name) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT feed_url FROM rss_sources WHERE status = 'active'")  # Adjust the query as needed
        sources = cursor.fetchall()
        return [source[0] for source in sources]  # Return a list of feed URLs

if __name__ == "__main__":
    initialize_database()
