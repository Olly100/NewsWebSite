"""
Module: publish.py
Purpose: To publish out the RSS feeds.
"""

from flask import Flask

def create_app():
       app = Flask(__name__)
       # Additional app configuration goes here
       return app