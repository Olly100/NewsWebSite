import asyncio
from unittest.mock import patch, AsyncMock
from parsing.parse_data import parse_feed, store_parsed_articles

@patch("ingestion.fetch_rss.fetch_rss", new_callable=AsyncMock)
@patch("parsing.parse_data.store_parsed_articles")
def test_pipeline(mock_store, mock_fetch):
    # Mock fetched data with 1 valid and 1 invalid entry
    mock_fetch.return_value = [
        {"title": "Valid Article", "link": "http://example.com", "published": "2024-01-01"},
        {"title": "", "link": None, "published": "2024-01-02"},  # Invalid article
    ]
    mock_store.return_value = None

    # Fetch RSS data using the mock
    fetched_data = asyncio.run(mock_fetch())
    print(f"Fetched data count: {len(fetched_data)}")  # Check how many items were fetched
    print(f"First fetched article (truncated): {fetched_data[0]['title'][:50]}")  # Check first article

    # Ensure data was fetched and parsed correctly
    assert len(fetched_data) > 0, "Fetched data should not be empty"

    # Parse the fetched data
    parsed_articles = parse_feed(fetched_data)
    print(f"Parsed articles count: {len(parsed_articles)}")  # Check how many articles were parsed
    if parsed_articles:
        print(f"First parsed article (truncated): {parsed_articles[0]['title'][:50]}")  # Check first parsed article

    # Ensure only 1 article is parsed
    assert len(parsed_articles) == 1, f"Should parse exactly one article, got {len(parsed_articles)}"

    # Store parsed articles
    store_parsed_articles(parsed_articles)

    # Ensure store_parsed_articles was called once with the correct arguments
    mock_store.assert_called_once_with(parsed_articles)

# Run the test function
test_pipeline()
