import validators
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from src.constants.http_status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_201_CREATED
from src.database import db
from src.models.user import User

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.post('/register')
def register():
    username = request.json.get('username', '')
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    if not username or not email or not password:
        return jsonify({'err': 'Missing username, email or password'}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'err': "Username is too short"}), HTTP_400_BAD_REQUEST

    if len(password) < 6:
        return jsonify({'err': "Password is too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({'err': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'err': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'err': "Email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'err': "Username is already taken"}), HTTP_409_CONFLICT

    password_hash = generate_password_hash(password)

    user = User(username=username, email=email, password=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({'msg': 'User created', 'user': {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }}), HTTP_201_CREATED

@auth.post('/login')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    if not email or not password:
        return jsonify({'err': 'Missing email or password'}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'err': "Email is not valid"}), HTTP_400_BAD_REQUEST

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({'err': "User does not exist"}), HTTP_401_UNAUTHORIZED

    if not check_password_hash(user.password, password):
        return jsonify({'err': "Email or Password is incorrect"}), HTTP_401_UNAUTHORIZED

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({'msg': 'User logged in', 'user': {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'username': user.username,
        'email': user.email
    }}), HTTP_200_OK

@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    return jsonify({'msg': 'User infomation', 'user': {'username': user.username, 'email': user.email}}), HTTP_200_OK

@auth.get('/refresh')
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)

    return jsonify({'msg': 'Refresh token', 'access_token': access_token}), HTTP_200_OK