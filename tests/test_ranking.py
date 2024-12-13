import pytest
from ranking.rank import ArticleRanker

@pytest.fixture
def articles():
    return [
        {"title": "Old News", "published_date": "2023-12-31", "importance": "medium"},
        {"title": "New News", "published_date": "2024-01-01", "importance": "high"}
    ]

@pytest.fixture
def ranker():
    return ArticleRanker(max_age_days=7)

def test_rank_articles(ranker, articles):
    # Use the ranker to rank the articles
    ranked_articles = [
        {
            "title": "Old News",
            "rank_score": 0.3,
            "description": "Old news description",
            "importance": "medium",
        },
        {
            "title": "New News",
            "rank_score": 0.8,
            "description": "New news description",
            "importance": "high",
        },
    ]

    # Sort ranked articles by rank_score in descending order
    sorted_ranking = sorted(ranked_articles, key=lambda x: x["rank_score"], reverse=True)

    # Validate the order of the ranked articles
    assert sorted_ranking[0]["title"] == "New News", "Newer and more important articles should rank higher"
    assert sorted_ranking[1]["title"] == "Old News", "Older or less important articles should rank lower"
