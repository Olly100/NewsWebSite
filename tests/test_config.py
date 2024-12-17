from config.settings import Config

def test_config_values():
    assert Config.DB_URL == "sqlite:///news_ingestion.db"
    assert Config.LOG_LEVEL == "INFO"
    assert Config.RSS_FEED_URL == "https://example.com/rss"
