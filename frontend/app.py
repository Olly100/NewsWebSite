import logging
from flask import Flask, render_template, jsonify
import sqlite3

def create_app(db_path='news_ingestion.db'):
    app = Flask(__name__)

    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Change to WARNING or ERROR

    # Helper function to fetch articles from the database
    def fetch_articles_from_db():
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT title, description, source, link, published_date FROM parsed_articles")
            articles = cursor.fetchall()
            print("ARTICLES are ", articles)
            return [
                {"title": row[0], "description": row[1], "source": row[2], "link": row[3], "published_date": row[4]}
                for row in articles
            ]

    @app.route('/')
    def index():
        # Use the helper function to fetch articles
        articles = fetch_articles_from_db()
        return render_template('index.html', articles=articles)

    @app.route('/api/articles', methods=['GET'])
    def api_articles():
        # Use the helper function to fetch articles
        articles = fetch_articles_from_db()
        return jsonify(articles)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

