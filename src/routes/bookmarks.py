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

        return jsonify({'msg':'Bookmark created', 'data': {
            'id': bookmark.id,
            'body': bookmark.body,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }}), HTTP_201_CREATED
    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        data = []

        bookmarks = Bookmark.query.filter_by(user_id = current_user).paginate(page, per_page)

        for bookmark in bookmarks.items:
            data.append({
                'id': bookmark.id,  
                'body': bookmark.body,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at
            })

        meta = {
            'page': bookmarks.page,
            'pages': bookmarks.pages,
            'total_count': bookmarks.total,
            'prev_page': bookmarks.prev_num,
            'next_page': bookmarks.next_num,
            'has_prev': bookmarks.has_prev,
            'has_next': bookmarks.has_next
        }

        return jsonify({'msg': 'Bookmarks found', 'data': data, 'meta': meta}), HTTP_200_OK

@bookmarks.route('/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id = id, user_id = current_user).first()
    
    if not bookmark:
        return jsonify({'err': 'Bookmark not found'}), HTTP_400_BAD_REQUEST
    
    if request.method == 'GET':
        return jsonify({'msg':'Bookmark found', 'data': {
                    'id': bookmark.id,
                    'body': bookmark.body,
                    'url': bookmark.url,
                    'short_url': bookmark.short_url,
                    'visits': bookmark.visits,
                    'created_at': bookmark.created_at,
                    'updated_at': bookmark.updated_at
                }}), HTTP_200_OK

    if request.method == 'PUT':
        body = request.json.get('body', '')
        url = request.json.get('url', '')

        if not validators.url(url):
            return jsonify({'err': "URL is not valid"}), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({'err': "URL is already bookmarked"}), HTTP_409_CONFLICT

        bookmark.body = body
        bookmark.url = url

        db.session.commit()

        return jsonify({'msg':'Bookmark updated', 'data': {
            'id': bookmark.id,
            'body': bookmark.body,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }}), HTTP_200_OK
    
    if request.method == 'DELETE':
        db.session.delete(bookmark)
        db.session.commit()

        return jsonify({'msg':'Bookmark deleted'}), HTTP_200_OK

@bookmarks.get('/stats')
@jwt_required()
def stats():
    current_user = get_jwt_identity()
    data = []

    items = Bookmark.query.filter_by(user_id = current_user).all()

    for item in items:
        new_link = {
            'id': item.id,
            'visits': item.visits,
            'url': item.url,
            'short_url': item.short_url,
        }

        data.append(new_link)
    
    return jsonify({'message': 'Stats found', 'data': data}), HTTP_200_OK