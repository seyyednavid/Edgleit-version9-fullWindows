"""
This module defines SQLAlchemy models for storing application settings.
"""

from appContents import db;


class Settings(db.Model):
    """
    SQLAlchemy model for storing application settings.

    Attributes:
        id (int): Primary key identifying the setting.
        flashspeededgelit (str): Speed of flashing for edge-lit buttons.
        numofflashes (str): Number of flashes for edge-lit buttons.
        on_color (str): Color code for the 'on' state of buttons.
        off_color (str): Color code for the 'off' state of buttons.
        free_color (str): Color code for indicating availability.
        busy_color (str): Color code for indicating busy state.
    """
    id = db.Column(db.Integer, primary_key=True)
    flashspeededgelit = db.Column(db.String(10))
    numofflashes = db.Column(db.String(10))
    on_color = db.Column(db.String(10))
    off_color = db.Column(db.String(10))
    free_color = db.Column(db.String(10))
    busy_color = db.Column(db.String(10))
    
    def __repr__(self):
        return f'Setting {self.id}'