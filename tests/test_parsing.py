import pytest
from parsing.parse_data import parse_feed, store_parsed_articles
import sqlite3

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_db.sqlite"
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE parsed_articles (
            title TEXT,
            description TEXT,
            source TEXT,
            published_date TEXT,
            parsed_at TEXT
        )
    ''')
    connection.commit()
    yield db_file
    connection.close()

def test_parse_feed():
    # Test feed with one valid and one invalid entry
    sample_feed_entries = [
    {"title": "Valid Title", "summary": "Valid Summary", "link": "http://example.com", "published": "2024-01-01"},
    {"title": "", "summary": "Invalid Article", "link": None, "published": "2024-01-02"},
]
    parsed = parse_feed(sample_feed_entries)
    assert len(parsed) == 1, f"Expected 1 valid article, got {len(parsed)}"
    assert parsed[0]["title"] == "Valid Title"

def test_store_parsed_articles(temp_db):
    articles = [{"title": "Article", "description": "Description", "link": "http://link", "published": "2024-01-01"}]
    store_parsed_articles(articles, db_name=temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM parsed_articles")
    count = cursor.fetchone()[0]
    assert count == 1