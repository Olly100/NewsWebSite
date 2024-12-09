import feedparser

def test_feedparser_valid_feed():
    feed_url = "http://example.com/rss"  # Replace with a real feed URL for testing
    feed = feedparser.parse(feed_url)
    assert feed.bozo == 0, "Feed should parse without errors"
    assert len(feed.entries) > 0, "Feed should contain entries"
    assert "title" in feed.entries[0], "Each entry should have a title"

def test_feedparser_invalid_feed():
    feed_url = "http://example.com/invalid_rss"
    feed = feedparser.parse(feed_url)
    assert feed.bozo != 0, "Feedparser should flag an invalid RSS feed"
