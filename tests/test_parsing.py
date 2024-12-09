from parsing.parse_data import parse_feed_entry  # Correct import statement

def test_parse_feed_entry():
    sample_entry = {
        "title": "Sample News Title",
        "description": "This is a test description.",
        "published": "Mon, 01 Jan 2024 10:00:00 GMT",
        "link": "http://example.com/article"
    }
    parsed_entry = parse_feed_entry(sample_entry)
    
    assert parsed_entry["title"] == "Sample News Title", "Title should be correctly parsed"
    assert parsed_entry["description"] == "This is a test description.", "Description should be correctly parsed"
    assert parsed_entry["date"] == "2024-01-01", "Date should be normalized to YYYY-MM-DD"
    assert parsed_entry["source"] == "example.com", "Source should be extracted from the URL"
