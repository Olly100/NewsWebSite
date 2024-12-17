"""
Module: rank.py
Purpose: Calculate article rankings based on time and importance
"""
import logging
from datetime import datetime
import sqlite3
import os

logger = logging.getLogger(__name__)

class ArticleRanker:
    """Calculate and manage article rankings"""
    
    IMPORTANCE_WEIGHTS = {
        'high': 1.0,
        'medium': 0.6,
        'low': 0.3,
        'uncategorized': 0.1
    }
    
    def __init__(self, max_age_days=7):
        """
        Initialize ranker with maximum age for articles
        
        Args:
            max_age_days: Number of days after which article score drops to near zero
        """
        self.max_age_days = max_age_days
    
    def fetch_articles_from_db(self, db_name: str) -> list:
        """
        Fetch articles from the database.
        
        Args:
            db_name: Path to the database file
            
        Returns:
            list: List of articles fetched from the database
        """
        articles = []
        try:
            # Get absolute path to the database
            if not os.path.isabs(db_name):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                db_name = os.path.join(project_root, db_name)
            
            abs_db_path = os.path.abspath(db_name)
            logger.info(f"Attempting to connect to database at: {abs_db_path}")
            
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT id, title, description, source, link, published_date, importance, derived_summary, keywords FROM parsed_articles')
                articles = cursor.fetchall()
                logger.info(f"Fetched {len(articles)} articles from database")
                
                if not articles:
                    logger.warning("No articles found in database")
                    return []
                
                # Convert fetched articles to a list of dictionaries
                articles = [
                    {
                        'id': article[0],
                        'title': article[1],
                        'description': article[2],
                        'source': article[3],
                        'link': article[4],
                        'published_date': article[5],
                        'importance': article[6],
                        'derived_summary': article[7] or article[2][:100] + "...",
                        'keywords': article[8]
                    }
                    for article in articles
                ]
                
        except Exception as e:
            logger.error(f"Error fetching articles from database: {e}")
            raise  # Raise the exception for handling in the calling method
        
        return articles

    def calculate_time_score(self, published_date: str) -> float:
        """
        Calculate time-based score (1.0 for now, decreasing to 0.0 for max_age)
        
        Args:
            published_date: Article publication date string (format: "%d %b %Y %H:%M")
            
        Returns:
            float: Score between 0 and 1
        """
        try:
            pub_date = datetime.strptime(published_date, "%d %b %Y %H:%M")
            now = datetime.now()
            age_days = (now - pub_date).total_seconds() / (24 * 3600)  # Convert to days
            
            if age_days < 0:  # Future dates get full score
                return 1.0
            
            # Linear decay over max_age_days
            time_score = 1.0 - (age_days / self.max_age_days)
            return max(0.0, min(1.0, time_score))  # Clamp between 0 and 1
            
        except ValueError as e:
            logger.error(f"Error parsing date {published_date}: {e}")
            return 0.0
    
    def calculate_importance_score(self, importance: str = None) -> float:
        """
        Convert importance level to numerical score
        
        Args:
            importance: Importance level string ('high', 'medium', 'low', 'uncategorized')
            
        Returns:
            float: Score between 0 and 1
        """
        importance = (importance or 'uncategorized').lower()
        return self.IMPORTANCE_WEIGHTS.get(importance, 0.1)
    
    def calculate_rank(self, published_date: str, importance: str) -> float:
        """
        Calculate overall rank score for an article
        
        Args:
            published_date: Article publication date
            importance: Article importance level
            
        Returns:
            float: Final rank score between 0 and 1
        """
        time_score = self.calculate_time_score(published_date)
        importance_score = self.calculate_importance_score(importance)
        
        # Equal weighting between time and importance
        rank = (time_score + importance_score) / 2
        
        return round(rank, 3)
    
    def rank_articles(self, articles: list) -> list:
        """
        Rank a list of articles based on their publication date and importance.
        
        Args:
            articles: List of articles to rank
            
        Returns:
            list: Ranked articles sorted by score
        """
        ranked_articles = []
        try:
            for article in articles:
                rank = self.calculate_rank(article['published_date'], article.get('importance'))
                article['rank'] = rank
                ranked_articles.append(article)
            
            # Sort by rank descending
            ranked_articles.sort(key=lambda x: x['rank'], reverse=True)
            logger.info(f"Ranked {len(ranked_articles)} articles")
            return ranked_articles
            
        except Exception as e:
            logger.error(f"Error ranking articles: {e}")
            if os.getenv('ENV', 'production') == 'development':
                raise  # Raise the exception in development mode
            return []

def get_ranked_articles(max_age_days=7, db_name="news_ingestion.db"):
    """
    Convenience function to get ranked articles
    
    Args:
        max_age_days: Number of days to consider for time decay
        db_name: Path to the database file
        
    Returns:
        list: Ranked articles sorted by score
    """
    # Ensure max_age_days is an integer
    max_age_days = int(max_age_days)
    ranker = ArticleRanker(max_age_days=max_age_days)
    
    # Fetch articles from the database
    articles = ranker.fetch_articles_from_db(db_name)
    
    # Rank the fetched articles
    return ranker.rank_articles(articles)

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    ranked_articles = get_ranked_articles(max_age_days=7)
    
    print("\nRanked Articles (from highest to lowest rank):")
    print("-" * 80)
    for article in ranked_articles:
        print(f"\nRank Score: {article['rank']:.3f}")
        print(f"Title: {article['title']}")
        print(f"Published: {article['published_date']}")
        print(f"Importance: {article['importance']}")
        print(f"Derived Summary: {article['derived_summary']}")
        print("-" * 80)
    
    print(f"\nTotal articles ranked: {len(ranked_articles)}")