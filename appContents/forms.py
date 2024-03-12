"""
This module defines Flask forms for user sign-in functionality.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


class SignInForm(FlaskForm):
    """
    Sign-in form for user authentication.
    """
    username = StringField(label='User Name:') # Field for entering the username
    password = PasswordField(label='Password:') # Field for entering the password
    submit = SubmitField(label='Sign in') # Submit button for signing in