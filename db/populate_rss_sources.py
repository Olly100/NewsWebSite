import sqlite3

def populate_rss_sources(db_name="news_ingestion.db"):
    # Define RSS feeds to insert
    rss_feeds = [
        ('https://www.prnewswire.co.uk/rss/news-releases-list.rss', 'PRNewswire', 'News', 'RSS', 'active'),
        ('https://feeds.bbci.co.uk/news/rss.xml', 'BBC', 'News', 'RSS', 'active'),
        ('https://www.theverge.com/rss/index.xml', 'The Verge', 'Technology', 'RSS', 'active'),
    ]

    # Connect to SQLite database
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Insert or update feeds
    for feed_url, source_name, category, feed_type, status in rss_feeds:
        try:
            # Try to insert a new feed
            cursor.execute('''
                INSERT INTO rss_sources (feed_url, source_name, category, feed_type, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (feed_url, source_name, category, feed_type, status))
            print(f"Added new feed: {feed_url}")
        except sqlite3.IntegrityError:
            # If the feed already exists, optionally update it
            cursor.execute('''
                UPDATE rss_sources
                SET source_name = ?, category = ?, feed_type = ?, status = ?
                WHERE feed_url = ?
            ''', (source_name, category, feed_type, status, feed_url))
            print(f"Updated existing feed: {feed_url}")

    # Commit changes and close connection
    connection.commit()
    connection.close()
    print("RSS sources populated successfully!")

if __name__ == "__main__":
    populate_rss_sources()
