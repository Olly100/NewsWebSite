from decouple import config

# Example configurations
DB_URL = config('DB_URL', default='sqlite:///default.db')  # Default to a SQLite database
LOG_LEVEL = config('LOG_LEVEL', default='INFO')  # Default log level
RSS_FEED_URL = config('RSS_FEED_URL', default='https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml')  # Example RSS feed URL
