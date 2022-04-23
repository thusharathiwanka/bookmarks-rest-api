import string
import random
from datetime import datetime
from src.database import db

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=True)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(), default=datetime.now())

    def generate_short_url(self):
        characters = string.digits + string.ascii_letters
        picked_characters = ''.join(random.choices(characters, k=3))

        link = self.query.filter_by(short_url=picked_characters).first()

        if link:
            self.generate_short_url()
        else:
          return picked_characters

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.short_url = self.generate_short_url()

    def __repr__(self) -> str:
        return 'Bookmark>>> {self.url}'