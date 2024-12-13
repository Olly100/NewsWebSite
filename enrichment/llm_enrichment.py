"""
Module: llm_enrichment.py
Purpose: Enrich articles with keywords and summaries using LLM
"""
from abc import ABC, abstractmethod
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class LLMEnricher(ABC):
    """Abstract base class for LLM enrichment services"""
    
    # Class constant for summary length
    MAX_SUMMARY_WORDS = 5
    
    @abstractmethod
    async def enrich_content(self, title: str, description: str, max_words: int = MAX_SUMMARY_WORDS) -> tuple[str, str, str]:
        """
        Get keyword, importance, and summary in a single API call
        
        Args:
            title: Article title
            description: Article description
            max_words: Maximum words for summary
            
        Returns:
            tuple: (keyword, importance, summary)
        """
        pass

class AnthropicEnricher(LLMEnricher):
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
    
    async def enrich_content(self, title: str, description: str, max_words: int = LLMEnricher.MAX_SUMMARY_WORDS) -> tuple[str, str, str]:
        """
        Get keyword, importance, and summary in a single API call
        
        Args:
            title: Article title
            description: Article description
            max_words: Maximum words for summary
            
        Returns:
            tuple: (keyword, importance, summary)
        """
        try:
            prompt = (
                "Analyze the following article and provide three things:\n"
                "1. A single category keyword (like 'politics', 'sports', 'technology')\n"
                "2. Importance level ('high', 'medium', 'low') based on news impact and urgency\n"
                f"3. A concise summary in {max_words} words or less\n\n"
                f"Title: {title}\n"
                f"Description: {description}\n\n"
                "Respond in exactly 3 lines:\n"
                "Line 1: just the keyword\n"
                "Line 2: just the importance level\n"
                "Line 3: the summary"
            )
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=250,
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Split response into three parts
            lines = response.content[0].text.strip().split('\n')
            keyword = lines[0].strip().lower()
            importance = lines[1].strip().lower()
            summary = lines[2].strip() if len(lines) > 2 else description[:100] + "..."
            
            return keyword, importance, summary
            
        except Exception as e:
            logger.error(f"Error enriching content with Anthropic: {e}")
            return "uncategorized", "low", description[:100] + "..."

async def enrich_articles(articles: list, enricher: LLMEnricher) -> list:
    """
    Enrich a list of articles with keywords, importance, and summaries
    
    Args:
        articles: List of article dictionaries
        enricher: LLM enrichment service instance
    
    Returns:
        List of enriched article dictionaries
    """
    enriched_articles = []
    
    for article in articles:
        try:
            # Get all enrichments in one call
            keyword, importance, summary = await enricher.enrich_content(
                article["title"],
                article["description"]
            )
            
            article["keywords"] = keyword
            article["importance"] = importance
            article["derived_summary"] = summary
            enriched_articles.append(article)
            
        except Exception as e:
            logger.error(f"Error enriching article {article.get('title')}: {e}")
            article["keywords"] = "uncategorized"
            article["importance"] = "low"
            article["derived_summary"] = article["description"][:100] + "..."
            enriched_articles.append(article)
    
    return enriched_articles 