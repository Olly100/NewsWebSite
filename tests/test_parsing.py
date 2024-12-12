import pytest
from parsing.parse_data import parse_feed, store_parsed_articles
import sqlite3

@pytest.fixture
def temp_db(tmp_path):
    # Create a temporary SQLite database for testing
    db_file = tmp_path / "test_db.sqlite"
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE parsed_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            source TEXT,
            link TEXT,
            published_date TIMESTAMP,
            parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    yield str(db_file)  # Provide the database file path to the test
    connection.close()  # Close the connection after the test

def test_parse_feed():
    # Test feed with one valid and one invalid entry
    sample_feed_entries = [
        {"title": "Valid Title", "summary": "Valid Summary", "link": "http://example.com", "published": "2024-01-01"},
        {"title": "", "summary": "Invalid Article", "link": None, "published": "2024-01-02"},
    ]
    parsed = parse_feed(sample_feed_entries)
    assert len(parsed) == 1, f"Expected 1 valid article, got {len(parsed)}"
    assert parsed[0]["title"] == "Valid Title"

def test_parse_feed_with_missing_fields():
    # Test feed with missing or malformed fields
    sample_feed_entries = [
        {"title": None, "summary": None, "link": None, "published": None},
        {"title": "Valid Title", "summary": "Valid Summary", "link": "http://example.com", "published": "2024-01-01"},
    ]
    parsed = parse_feed(sample_feed_entries)
    assert len(parsed) == 1, "Should parse only valid articles"
    assert parsed[0]["title"] == "Valid Title", "The title of the valid article should be 'Valid Title'"

def test_parse_feed_malformed_data():
    # Explicitly test malformed data formats
    malformed_feed_entries = [{"malformed_field": "Unexpected Data"}]
    parsed = parse_feed(malformed_feed_entries)
    assert len(parsed) == 0, "Malformed entries should not be parsed"

def test_store_parsed_article_content(temp_db):
    # Test storing parsed articles and verify stored data integrity
    articles = [
        {
            "title": "Test Article",
            "description": "Test Description",
            "link": "http://link",  # Ensure this value is not None
            "published_date": "2024-01-01",
            "source": "Test Source"
        }
    ]
    store_parsed_articles(articles, db_name=temp_db)  # Use the imported function
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, description, source, link, published_date FROM parsed_articles")
        row = cursor.fetchone()
        assert row == ("Test Article", "Test Description", "Test Source", "http://link", "2024-01-01"), "Stored article data does not match input data"

def test_store_parsed_articles(temp_db):
    articles = [
        {
            "title": "Article 1",
            "description": "Description 1",
            "link": "http://link1",
            "published_date": "2024-01-02",
            "source": "Source 1"
        },
        {
            "title": "Article 2",
            "description": "Description 2",
            "link": "http://link2",
            "published_date": "2024-01-03",
            "source": "Source 2"
        }
    ]
    store_parsed_articles(articles, db_name=temp_db)
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parsed_articles")
        count = cursor.fetchone()[0]
        assert count == 2, "Expected 2 articles to be stored in the database"