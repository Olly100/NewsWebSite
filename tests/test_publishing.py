import pytest
import sqlite3
from frontend.app import create_app  # Ensure create_app exists in app.py
from parsing.parse_data import store_parsed_articles  # Ensure parse_data module exists

@pytest.fixture
def app(temp_db):
    app = create_app(db_path=temp_db)  # Ensure create_app accepts db_path as a parameter
    app.config["TESTING"] = True
    return app

@pytest.fixture
def temp_db(tmp_path):
    # Create a temporary SQLite database for testing
    db_file = tmp_path / "test_db.sqlite"
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE parsed_articles (
            title TEXT NOT NULL,
            description TEXT,
            source TEXT NOT NULL,
            link TEXT,
            published_date TEXT,
            parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    yield str(db_file)  # Provide the database file path to the test
    connection.close()  # Close the connection after the test

def add_article_to_db(article_data, db_file):
    # Helper function to add an article to the database
    with sqlite3.connect(str(db_file)) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO parsed_articles (title, description, source, published_date)
            VALUES (?, ?, ?, ?)
        ''', (article_data["title"], article_data["description"], article_data["source"], "2024-01-01"))
        connection.commit()

def test_homepage_rendering(app):
    # Test homepage rendering with no articles
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200, "Homepage should render successfully"
        assert b'<h1 class="text-center text-primary mb-4">News Articles</h1>' in response.data, "Homepage should contain the main heading"

def test_empty_database_handling(app):
    # Test behavior when the database is empty
    with app.test_client() as client:
        response = client.get("/")
        assert b"No articles available" in response.data, "Homepage should indicate no articles are available"

@pytest.mark.parametrize("article_data", [
    {"title": "Title 1", "description": "Description 1", "source": "Source 1"},
    {"title": "Title 2", "description": "Description 2", "source": "Source 2"}
])
def test_publishing_with_articles(article_data, temp_db, app):
    # Add article to the database
    add_article_to_db(article_data, temp_db)

    # Verify that the article is in the database
    with sqlite3.connect(temp_db) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM parsed_articles")
        db_contents = cursor.fetchall()

    # Assert that the article was added
    assert any(row[0] == article_data["title"] for row in db_contents), (
        f"Expected article with title '{article_data['title']}' to be in the database"
    )

    # Simulate a request to the root URL and check the response
    with app.test_client() as client:
        response = client.get("/")
        assert article_data["title"].encode() in response.data, (
            f"Expected article title '{article_data['title']}' to be in response"
        )

def test_store_parsed_article_content(temp_db):
    articles = [
        {
            "title": "Test Article",
            "description": "Test Description",
            "link": "http://link",  # Ensure this value is correct
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
