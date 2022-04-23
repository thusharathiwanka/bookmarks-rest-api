import validators
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from src.models.bookmark import Bookmark
from src.database import db

bookmarks = Blueprint('bookmarks', __name__, url_prefix='/api/v1/bookmarks')

@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def index():
    current_user = get_jwt_identity()
    
    if request.method == 'POST':
        body = request.json.get('body', '')
        url = request.json.get('url', '')

        if not validators.url(url):
            return jsonify({'err': "URL is not valid"}), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({'err': "URL is already bookmarked"}), HTTP_409_CONFLICT

        bookmark = Bookmark(body = body, url = url, user_id = current_user) 

        db.session.add(bookmark)
        db.session.commit()

        return jsonify({'msg':'Bookmark created', 'bookmark': {
            'id': bookmark.id,
            'body': bookmark.body,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }}), HTTP_201_CREATED
    else:
        bookmarks = Bookmark.query.filter_by(user_id = current_user).all()

        data = []

        for bookmark in bookmarks:
            data.append({
                'id': bookmark.id,
                'body': bookmark.body,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at
            })

        return jsonify({'bookmarks': data}), HTTP_200_OK