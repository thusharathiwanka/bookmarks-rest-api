import os
from flask import Flask, redirect
from flask_jwt_extended import JWTManager
from src.constants.http_status_codes import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.database import db
from src.routes.auth import auth
from src.routes.bookmarks import bookmarks
from src.models.bookmark import Bookmark

def create_app(test_config = None):
  app = Flask(__name__, instance_relative_config = True)

  if test_config is None:
    app.config.from_mapping(SECRET_KEY = os.environ.get('SECRET_KEY'), SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI'), SQLALCHEMY_TRACK_MODIFICATIONS = False, JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY'))
  else:
    app.config.from_mapping(test_config)

  db.app = app
  db.init_app(app)

  JWTManager(app)

  app.register_blueprint(auth)
  app.register_blueprint(bookmarks)

  @app.get('/<string:short_url>')
  def redirect_to_long_url(short_url):
    bookmark = Bookmark.query.filter_by(short_url = short_url).first()

    if not bookmark:
      return {'err': 'Bookmark not found'}, 404
  
    bookmark.visits += 1
    db.session.commit()

    return redirect(bookmark.url)

  @app.errorhandler(HTTP_404_NOT_FOUND)
  def handle_404(error):
    return {'err': 'Not found'}, HTTP_404_NOT_FOUND

  @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
  def handle_500(error):
    return {'err': 'Something went wrong'}, HTTP_500_INTERNAL_SERVER_ERROR

  return app