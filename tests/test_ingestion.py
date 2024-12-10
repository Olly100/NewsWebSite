from unittest.mock import patch, MagicMock
import pytest
import feedparser

@patch("feedparser.parse")
def test_feedparser_valid_feed(mock_parse):
    mock_parse.return_value = MagicMock(bozo=0, entries=[{"title": "Title"}])
    feed = feedparser.parse("http://example.com/rss")
    assert feed.bozo == 0
    assert len(feed.entries) > 0
    assert "title" in feed.entries[0]

@patch("feedparser.parse")
def test_feedparser_invalid_feed(mock_parse):
    mock_parse.return_value = MagicMock(bozo=1, entries=[])
    feed = feedparser.parse("http://example.com/invalid_rss")
    assert feed.bozo != 0