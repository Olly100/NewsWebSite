# News Aggregation and Publishing System

## Overview
This project is a modular application that ingests, parses, ranks, and publishes news articles from RSS feeds. It provides a foundation for further expansion into a scalable, user-focused news aggregation platform.

## Features
- **RSS Feed Ingestion**: Fetches articles from multiple RSS feeds asynchronously.
- **Data Parsing**: Extracts and normalizes key fields (e.g., title, description, source) from the fetched data.
- **Database Storage**: Stores parsed articles in an SQLite database, ensuring data integrity and easy retrieval.
- **Ranking Logic**: Implements ranking algorithms to prioritize articles based on defined criteria.
- **Publishing**: Publishes processed articles to a web interface.
- **Testing Framework**: Comprehensive unit tests using `pytest` to ensure code reliability.

## Project Structure
/news_aggregation
│
├── db/
│ ├── database.py # Database connection and operations
│ ├── populate_rss_sources.py # Script to populate RSS sources in the database
│
├── ingestion/
│ ├── fetch_rss.py # Fetching RSS feeds asynchronously
│
├── parsing/
│ ├── parse_data.py # Parsing logic for RSS feed data
│
├── ranking/
│ ├── rank.py # Ranking articles based on defined rules
│
├── publishing/
│ ├── publish.py # Handles publishing to the output medium
│
├── frontend/
│ ├── app.py # Flask application for serving articles
│ ├── templates/
│ ├── index.html # HTML template for displaying articles
│
├── tests/
│ ├── test_parsing.py # Unit tests for parsing functionality
│ ├── test_pipeline.py # Integration tests for the pipeline
│ ├── test_publishing.py # Tests for publishing articles
│ ├── test_ingestion.py # Tests for RSS feed ingestion
│
├── main.py # Main entry point for the application
├── logging_config.py # Logging setup for debugging and monitoring
└── README.md # Project documentation


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/news_aggregation.git
   cd news_aggregation
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Setup Instructions

1. **Initialize the Database**:
   Run the following command to set up the database:
   ```bash
   python main.py --init-db
   ```

2. **Populate RSS Sources**:
   To populate the database with initial RSS sources, run:
   ```bash
   python db/populate_rss_sources.py
   ```

## Running the Application

To run the application, execute the following command:
bash
python main.py


Visit `http://127.0.0.1:5000` in your web browser to view the news articles.

## Testing

To run the tests, use the following command:
bash
pytest


## Logging

The application uses logging to track operations and errors. Logs are written to `app.log` and can be monitored for debugging purposes.

## Future Enhancements

- Implement user authentication for personalized news feeds.
- Expand the ranking algorithm to consider user preferences.
- Add support for additional data sources and formats.
- Improve the user interface for better interaction with the news articles.

## License

This project is licensed under the MIT License - see the LICENSE file for details.