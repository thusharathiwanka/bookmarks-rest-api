from flask import Blueprint, jsonify

bookmarks = Blueprint('bookmarks', __name__, url_prefix='/api/v1/bookmarks')

@bookmarks.get('/')
def index():
    return jsonify({'bookmarks': ['Bookmark1', 'Bookmark2', 'Bookmark3']})