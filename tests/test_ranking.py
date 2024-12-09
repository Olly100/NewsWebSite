from ranking.rank import rank_articles  # Import the specific function

def test_rank_articles():
    articles = [
        {"title": "Old News", "date": "2023-12-31"},
        {"title": "New News", "date": "2024-01-01"}
    ]
    ranked_articles = rank_articles(articles)
    
    assert ranked_articles[0]["title"] == "New News", "Newer articles should rank higher"
    assert ranked_articles[1]["title"] == "Old News", "Older articles should rank lower"
