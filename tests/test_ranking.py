import pytest
from ranking.rank import ArticleRanker
from datetime import datetime, timedelta

@pytest.fixture
def articles():
    return [
        {"title": "Old News", "published_date": "2023-12-31 12:00", "importance": "medium"},
        {"title": "New News", "published_date": "2024-01-01 12:00", "importance": "high"},
        {"title": "Future News", "published_date": "2024-01-02 12:00", "importance": "low"},
        {"title": "Uncategorized News", "published_date": "2023-12-30 12:00", "importance": None}
    ]

@pytest.fixture
def ranker():
    return ArticleRanker(max_age_days=7)

def test_rank_articles(ranker, articles):
    # Use the ranker to rank the articles
    ranked_articles = ranker.rank_articles(articles)
    
    # Sort ranked articles by rank in descending order
    sorted_ranking = sorted(ranked_articles, key=lambda x: x["rank"], reverse=True)

    # Validate the order of the ranked articles
    assert sorted_ranking[0]["title"] == "New News", "Newer and more important articles should rank higher"
    assert sorted_ranking[1]["title"] == "Old News", "Older or less important articles should rank lower"
    assert sorted_ranking[2]["title"] == "Uncategorized News", "Uncategorized articles should rank lower than others"
    assert sorted_ranking[3]["title"] == "Future News", "Future articles should not rank higher than past articles"

    # Validate rank_score logic
    assert sorted_ranking[0]["rank"] > sorted_ranking[1]["rank"], "Rank scores should decrease with relevance"

def test_calculate_time_score(ranker):
    recent_date = (datetime.now() - timedelta(days=2)).strftime("%d %b %Y %H:%M")
    assert ranker.calculate_time_score(recent_date) > 0.7, "Recent articles should have a high time score"

    old_date = (datetime.now() - timedelta(days=10)).strftime("%d %b %Y %H:%M")
    assert ranker.calculate_time_score(old_date) < 0.3, "Old articles should have a low time score"

    future_date = (datetime.now() + timedelta(days=2)).strftime("%d %b %Y %H:%M")
    assert ranker.calculate_time_score(future_date) == 1.0, "Future articles should have a full score"

def test_calculate_importance_score(ranker):
    assert ranker.calculate_importance_score("high") == 1.0, "High importance should score 1.0"
    assert ranker.calculate_importance_score("medium") == 0.6, "Medium importance should score 0.6"
    assert ranker.calculate_importance_score("low") == 0.3, "Low importance should score 0.3"
    assert ranker.calculate_importance_score("unknown") == 0.1, "Unknown importance should default to 0.1"
    assert ranker.calculate_importance_score(None) == 0.1, "None importance should default to 0.1"

def test_calculate_rank(ranker):
    assert ranker.calculate_rank("2024-01-01 12:00", "high") > ranker.calculate_rank("2023-12-31 12:00", "medium"), "Rank should reflect time and importance"
    assert ranker.calculate_rank("2023-12-31 12:00", None) == ranker.calculate_rank("2023-12-31 12:00", "uncategorized"), "None importance should be treated as uncategorized"
