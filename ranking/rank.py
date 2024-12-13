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
    
    def calculate_importance_score(self, importance: str) -> float:
        """
        Convert importance level to numerical score
        
        Args:
            importance: Importance level string ('high', 'medium', 'low', 'uncategorized')
            
        Returns:
            float: Score between 0 and 1
        """
        return self.IMPORTANCE_WEIGHTS.get(importance.lower(), 0.1)
    
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
    
    def rank_articles(self, db_name="news_ingestion.db") -> list:
        """
        Fetch and rank all articles from database
        """
        try:
            # Get absolute path to the database
            if not os.path.isabs(db_name):
                # If db_name is relative, make it relative to project root
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                db_name = os.path.join(project_root, db_name)
            
            abs_db_path = os.path.abspath(db_name)
            logger.info(f"Attempting to connect to database at: {abs_db_path}")
            
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                
                # First check if we have any articles
                cursor.execute('SELECT COUNT(*) FROM parsed_articles')
                count = cursor.fetchone()[0]
                logger.info(f"Found {count} articles in database")
                
                cursor.execute('''
                    SELECT id, title, description, source, link, 
                    published_date, importance, derived_summary, keywords 
                    FROM parsed_articles
                ''')
                articles = cursor.fetchall()
                logger.info(f"Fetched {len(articles)} articles from database")
                
                if not articles:
                    logger.warning("No articles found in database")
                    return []
                
                ranked_articles = []
                for article in articles:
                    id, title, description, source, link, published_date, importance, derived_summary, keywords = article
                    rank = self.calculate_rank(published_date, importance or 'uncategorized')
                    ranked_articles.append({
                        'id': id,
                        'title': title,
                        'description': description,
                        'source': source,
                        'link': link,
                        'published_date': published_date,
                        'importance': importance,
                        'derived_summary': derived_summary or description[:100] + "...",
                        'rank': rank
                    })
                
                # Sort by rank descending
                ranked_articles.sort(key=lambda x: x['rank'], reverse=True)
                logger.info(f"Ranked {len(ranked_articles)} articles")
                return ranked_articles
                
        except Exception as e:
            logger.error(f"Error ranking articles: {e}")
            logger.exception("Full traceback:")
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
    return ranker.rank_articles(db_name)

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    ranker = ArticleRanker(max_age_days=7)
    ranked_articles = ranker.rank_articles()
    
    print("\nRanked Articles (from highest to lowest rank):")
    print("-" * 80)
    for article in ranked_articles:
        print(f"\nRank Score: {article['rank']:.3f}")
        print(f"Title: {article['title']}")
        print(f"Published: {article['published_date']}")
        print(f"Importance: {article['importance']}")
        
        # Get the component scores for transparency
        time_score = ranker.calculate_time_score(article['published_date'])
        importance_score = ranker.calculate_importance_score(article['importance'] or 'uncategorized')
        print(f"Time Score: {time_score:.3f}")
        print(f"Importance Score: {importance_score:.3f}")
        print("-" * 80)
    
    print(f"\nTotal articles ranked: {len(ranked_articles)}")