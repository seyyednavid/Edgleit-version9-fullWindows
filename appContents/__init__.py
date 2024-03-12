"""
This script initializes a Flask application and defines routes and functionality for a web application.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import webbrowser
import subprocess
import pyautogui
import time
import os


# Initialize Flask application
app = Flask(__name__, static_folder='static')
# Configure Flask application
# Database URI configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# Secret key configuration
app.config['SECRET_KEY'] = "382860d6ef9587472b5f3bbe" # Read secret key from environment variable
# Initialize SQLAlchemy database
db = SQLAlchemy(app)

from appContents import models;
from appContents import websocket;
from appContents import routes;


def open_browser():
    """
    Opens the default web browser with the home page and enters fullscreen mode.
    """
    webbrowser.open(f'http://{os.getenv("COMBINED_FLASK_IP_PORT")}/callforward')
    time.sleep(2)
    # Simulate pressing the F11 key to enter fullscreen mode
    pyautogui.press('f11')
