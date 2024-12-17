from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from functools import wraps
import sqlite3
from datetime import datetime
import logging
import sys
import os
import json
from dotenv import load_dotenv
from pipeline.rss_manager import refresh_rss_feeds  # Import the new function
from enrichment.llm_enrichment import AnthropicEnricher  # Ensure this import is present

import asyncio

# Load environment variables before anything else
load_dotenv()

# Set up logging first
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.logging_config import setup_logging
print("App.py - System Path:", sys.path)
from config.settings import Config
from ranking.rank import get_ranked_articles

logger = setup_logging()

# Debug prints
print("Python path:", sys.path)
print("Current directory:", os.getcwd())
print("File location:", os.path.abspath(__file__))

# Verify environment variables are loaded
logger.info(f"Admin user set to: {Config.ADMIN_USERNAME}")
logger.info(f"Admin password set")

def create_app(db_path=None):
    """
    Factory function to create a Flask app instance with dynamic configuration.
    """
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key')
    app.config['DB_PATH'] = db_path or Config.DB_NAME

    # Basic auth decorator
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth = request.authorization
            if not auth:
                logger.warning("No auth credentials provided")
                return ('Could not verify your access level for that URL.\n'
                        'You have to login with proper credentials', 401,
                        {'WWW-Authenticate': 'Basic realm="Login Required"'})

            expected_username = Config.ADMIN_USERNAME
            expected_password = Config.ADMIN_PASSWORD

            if auth.username != expected_username or auth.password != expected_password:
                logger.warning("Authentication failed")
                if auth.username != expected_username:
                    logger.warning(f"Wrong username: {auth.username}")
                if auth.password != expected_password:
                    logger.warning("Wrong password")

                return ('Could not verify your access level for that URL.\n'
                        'You have to login with proper credentials', 401,
                        {'WWW-Authenticate': 'Basic realm="Login Required"'})

            return f(*args, **kwargs)
        return decorated_function

    @app.route('/')
    def index():
        try:
            logger.info("Starting to fetch ranked articles")
            ranked_articles = get_ranked_articles(max_age_days=7, db_name=app.config['DB_PATH'])
            logger.info(f"Got {len(ranked_articles)} ranked articles")

            if ranked_articles:
                logger.info(f"Sample article data: {ranked_articles[0]}")

            articles_for_display = []
            for article in ranked_articles:
                logger.debug(f"Processing article: {article.get('title')}")
                logger.debug(f"Summary: {article.get('derived_summary')}")
                articles_for_display.append({
                    'title': article['title'],
                    'derived_summary': article.get('derived_summary', article.get('description', '')[:100] + "..."),
                    'source': article.get('source', ''),
                    'link': article.get('link', ''),
                    'published_date': article['published_date'],
                    'importance': article['importance'],
                    'rank_score': article['rank'],
                })

            logger.info(f"Prepared {len(articles_for_display)} articles for display")
            return render_template('index.html', articles=articles_for_display)

        except Exception as e:
            logger.error(f"Error in index route: {e}")
            logger.exception("Full traceback:")
            return render_template('index.html', articles=[])

    @app.route('/api/articles', methods=['GET'])
    def api_articles():
        try:
            ranked_articles = get_ranked_articles(max_age_days=7, db_name=app.config['DB_PATH'])
            return jsonify(ranked_articles)
        except Exception as e:
            logger.error(f"Error fetching articles for API: {e}")
            return jsonify([])

    @app.route('/admin')
    @admin_required
    def admin():
        try:
            with sqlite3.connect(app.config['DB_PATH']) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT key, value, description, type, options FROM app_config')
                configs = [
                    {
                        'key': row[0],
                        'value': row[1],
                        'description': row[2],
                        'type': row[3],
                        'options': json.loads(row[4]) if row[4] else None
                    }
                    for row in cursor.fetchall()
                ]

                cursor.execute('SELECT id, feed_url, source_name, category, status FROM rss_sources')
                rss_sources = [
                    {
                        'id': row[0],
                        'feed_url': row[1],
                        'source_name': row[2],
                        'category': row[3],
                        'status': row[4]
                    }
                    for row in cursor.fetchall()
                ]

                return render_template('admin.html', configs=configs, rss_sources=rss_sources)

        except Exception as e:
            logger.error(f"Error in admin route: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/admin/config', methods=['POST'])
    @admin_required
    def update_config():
        try:
            updates = request.form.to_dict()

            with sqlite3.connect(app.config['DB_PATH']) as conn:
                cursor = conn.cursor()
                for key, value in updates.items():
                    cursor.execute('''
                        UPDATE app_config 
                        SET value = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE key = ?
                    ''', (value, key))

                conn.commit()

            flash('Configuration updated successfully', 'success')
            return redirect(url_for('admin'))

        except Exception as e:
            logger.error(f"Error updating config: {e}")
            flash(f'Error updating configuration: {str(e)}', 'error')
            return redirect(url_for('admin'))

    @app.route('/admin/rss', methods=['POST'])
    @admin_required
    def update_rss():
        try:
            action = request.form.get('action')

            if action == 'add':
                url = request.form.get('feed_url')
                name = request.form.get('source_name')
                category = request.form.get('category')

                with sqlite3.connect(app.config['DB_PATH']) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO rss_sources (feed_url, source_name, category)
                        VALUES (?, ?, ?)
                    ''', (url, name, category))

            elif action == 'update':
                id = request.form.get('id')
                status = request.form.get('status')

                with sqlite3.connect(app.config['DB_PATH']) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE rss_sources 
                        SET status = ?
                        WHERE id = ?
                    ''', (status, id))

            conn.commit()
            flash('RSS sources updated successfully', 'success')
            return redirect(url_for('admin'))

        except Exception as e:
            logger.error(f"Error updating RSS sources: {e}")
            flash(f'Error updating RSS sources: {str(e)}', 'error')
            return redirect(url_for('admin'))

    @app.route('/refresh_feeds', methods=['POST'])
    @admin_required  # Ensure this route is protected if needed
    def refresh_feeds():
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                flash("ANTHROPIC_API_KEY not found in environment variables.", "error")
                return redirect(url_for('admin'))

            # Initialize the enricher
            enricher = AnthropicEnricher(api_key)  # Ensure api_key is a string

            # Call the refresh_rss_feeds function from rss_manager
            result_message = asyncio.run(refresh_rss_feeds(enricher))
            flash(result_message, "success")
        except Exception as e:
            logger.error(f"Error refreshing feeds: {e}")
            flash(f"Error refreshing feeds: {str(e)}", "error")

        return redirect(url_for('admin'))  # Redirect back to the admin page

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)