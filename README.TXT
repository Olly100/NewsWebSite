News Website Project

Overview
This project is a news aggregation website that fetches articles from various RSS feeds, enriches them with keywords and summaries using a language model, and displays them to users. The application is built using Python with Flask for the web framework, SQLite for the database, and the Anthropic API for content enrichment.
Features
Fetches articles from multiple RSS feeds.
Parses and stores articles in a SQLite database.
Enriches articles with keywords, importance levels, and summaries using the Anthropic language model.
Displays enriched articles on the main page.
Admin interface for refreshing RSS feeds and managing articles.

Project Structure
/your_project
    /config
        config.py               # Configuration settings#
    /frontend
        app.py                  # Flask application and routes
        templates/              # HTML templates for rendering pages
    /enrichment
        llm_enrichment.py       # Contains the AnthropicEnricher class and enrichment logic
    /ingestion
        fetch_rss.py           # Fetches RSS feed data
    /parsing
        parse_data.py          # Parses and normalizes article data
    /pipeline
        rss_manager.py          # Manages the RSS feed refresh process
    /publishing
        publishing.py           # Manages the publishing of articles
    /db
        database.py             # Database setup and interaction
    /ranking
        ranking.py              # Manages the ranking of articles
    /scheduler
        fetch_schedule.py       # Scheduled RSS fetching
    /main
        main.py                 # Entry point for running the application
    /tests                      # series of tests for key components
    .env                        # Environment variables (e.g., API keys)
    requirements.txt            # Python package dependencies
    news_ingestion.db           # SQLite3 database
    README.md                   # Project documentation


Installation
1. Clone the repository:
   git clone https://github.com/yourusername/news-website.git
   cd news-website

2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install the required packages:
   pip install -r requirements.txt

4. Set up your environment variables in a .env file:
   ANTHROPIC_API_KEY=your_anthropic_api_key

5. Initialize the database:
   You can run the database setup function in main.py or call it directly in a Python shell.

Usage
1. Start the application:
   python main.py

2. Access the application in your web browser at http://127.0.0.1:5000.

Use the admin interface to refresh RSS feeds and manage articles.

Code Overview
Key Components
Frontend: The app.py file contains the Flask application and routes for handling requests and rendering templates.
Enrichment: The llm_enrichment.py file defines the AnthropicEnricher class, which uses the Anthropic API to enrich articles with keywords and summaries.
Ingestion: The fetch_rss.py file is responsible for fetching data from RSS feeds.
Parsing: The parse_data.py file handles the extraction and normalization of article fields.
Pipeline: The rss_manager.py file manages the process of refreshing RSS feeds, parsing articles, enriching them, and storing them in the database.
Database: The database.py file contains functions for setting up and interacting with the SQLite database.

Logging
The application uses Python's built-in logging module to log important events and errors. Logs are written to the console and can be configured to log to a file if desired.

Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.
License
This project is licensed under the MIT License. See the LICENSE file for more details.
---
Feel free to modify any sections to better fit your project's specifics or to add any additional information that may be relevant!