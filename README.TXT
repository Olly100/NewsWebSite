# News Aggregation and Publishing System

## Overview
This project is a modular application that ingests, parses, ranks, and publishes news articles from RSS feeds. It provides a foundation for further expansion into a scalable, user-focused news aggregation platform.

## Directory Structure
- `config.py`: Application configuration settings.
- `logging_config.py`: Logging setup for debugging and monitoring.
- `main.py`: Entry point for the application.
- `ingestion/`: Handles RSS feed fetching.
  - `fetch_rss.py`: Fetches and validates RSS feed data asynchronously.
- `parsing/`: Parses and normalizes the fetched RSS feed data.
  - `parse_data.py`: Extracts key fields (e.g., title, description) and stores articles in a database.
- `ranking/`: Implements ranking logic for parsed articles.
  - `rank.py`: Ranks articles based on defined rules.
- `publishing/`: Publishes processed data.
  - `publish.py`: Handles publishing to the output medium.
- `tests/`: Unit tests for the application modules.
  - Includes tests for ingestion, parsing, ranking, and publishing.

## Features Implemented
1. **Logging**:
   - Configured centralized logging for debugging and monitoring.
2. **Error Handling**:
   - Robust error handling for RSS feed ingestion and parsing.
   - Retry mechanism for transient errors during RSS feed fetching.
3. **Asynchronous RSS Feed Processing**:
   - Fetching RSS feeds using `aiohttp` for non-blocking I/O operations.
   - Parsing RSS feed entries with error handling for invalid feeds.
4. **Database Storage**:
   - Storing parsed articles in an SQLite database.
5. **Test Framework**:
   - Unit tests for each module using `pytest` to ensure code reliability.

## Setup Instructions
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the Database**:
   Run the following command to set up the database:
   ```bash
   python main.py --init-db
   ```

## Running the Application
To run the application, execute the following command:
```bash
python main.py
```

## Testing
To run the tests, use the following command:
```bash
pytest
```

## Future Enhancements
- Implement user authentication for personalized news feeds.
- Expand the ranking algorithm to consider user preferences.
- Add support for additional data sources and formats.
- Improve the user interface for better interaction with the news articles.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
