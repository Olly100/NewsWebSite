import sqlite3
import os

# Print current working directory
print(os.getcwd())

# Try to connect to the database and count articles
db_path = "news_ingestion.db"  # or whatever path you're using
print(f"Checking database at: {os.path.abspath(db_path)}")

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM parsed_articles")
    count = cursor.fetchone()[0]
    print(f"Found {count} articles")
    
    # Print a sample article
    cursor.execute("SELECT * FROM parsed_articles LIMIT 1")
    print("Sample article:", cursor.fetchone())