import validators
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_201_CREATED
from src.database import db
from src.models.user import User

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.post('/register')
def register():
    username = request.json.get('username', '')
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    if not username or not email or not password:
        return jsonify({'message': 'Missing username, email or password'}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': "Username is too short"}), HTTP_400_BAD_REQUEST

    if len(password) < 6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT

    password_hash = generate_password_hash(password)

    user = User(username=username, email=email, password=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'user created', 'user': {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }}), HTTP_201_CREATED

@auth.post('/login')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({'error': "User does not exist"}), HTTP_401_UNAUTHORIZED

    if not check_password_hash(user.password, password):
        return jsonify({'error': "Email or Password is incorrect"}), HTTP_401_UNAUTHORIZED

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({'message': 'user logged in', 'user': {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'username': user.username,
        'email': user.email
    }})

@auth.get('/me')
def me():
    return jsonify({'message': 'Me'})