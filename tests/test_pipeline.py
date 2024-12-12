import asyncio
from unittest.mock import patch, AsyncMock
from parsing.parse_data import parse_feed, store_parsed_articles
import pytest

@patch("ingestion.fetch_rss.fetch_rss", new_callable=AsyncMock)
async def test_fetch_rss_error(mock_fetch):
    # Simulate a fetch error by raising an exception
    mock_fetch.side_effect = Exception("Fetch failed")
    
    # Verify that the exception is raised when calling the mocked fetch_rss
    with pytest.raises(Exception, match="Fetch failed"):
        await mock_fetch()  # Use await since it's an async function

@patch("ingestion.fetch_rss.fetch_rss", new_callable=AsyncMock)
def test_empty_feed(mock_fetch):
    # Simulate an empty feed by returning an empty list
    mock_fetch.return_value = []
    
    # Parse the empty fetched data
    parsed_articles = parse_feed(mock_fetch.return_value)
    
    # Assert that no articles are parsed from an empty feed
    assert len(parsed_articles) == 0, "No articles should be parsed from an empty feed"

@patch("ingestion.fetch_rss.fetch_rss", new_callable=AsyncMock)
@patch("parsing.parse_data.store_parsed_articles")
async def test_pipeline(mock_store, mock_fetch):
    # Mock fetched data with 1 valid and 1 invalid entry
    mock_fetch.return_value = [
        {"title": "Valid Article", "link": "http://example.com", "published": "2024-01-01"},
        {"title": "", "link": None, "published": "2024-01-02"},  # Invalid article
    ]
    mock_store.return_value = None

    # Fetch RSS data using the mock
    fetched_data = await mock_fetch()  # Use await since it's an async function
    print(f"Fetched data count: {len(fetched_data)}")  # Check how many items were fetched

    # Ensure data was fetched and parsed correctly
    assert len(fetched_data) > 0, "Fetched data should not be empty"

    # Parse the fetched data
    parsed_articles = parse_feed(fetched_data)
    print(f"Parsed articles count: {len(parsed_articles)}")  # Check how many articles were parsed

    # Ensure only valid articles are parsed
    assert len(parsed_articles) == 1, f"Should parse exactly one article, got {len(parsed_articles)}"

    # Store parsed articles using the mock
    mock_store(parsed_articles)  # Call the mock instead of the actual function

    # Ensure store_parsed_articles was called once with the correct arguments
    mock_store.assert_called_once_with(parsed_articles)

# Run the test function
if __name__ == "__main__":
    asyncio.run(test_fetch_rss_error())
