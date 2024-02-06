import os
from urllib.parse import urlparse
import redis
from flask import Flask, g, session
from .models import db, User
from .forms import UserAddForm, UserSignupForm, LoginForm, UserEditForm, IdeaAddForm, GroupAddForm, KnowledgeSourceAddForm, KnowledgeDomainAddForm, KnowledgeBaseAddForm, KnowledgeBaseEditForm
from .celery_app import celery_init_app
from .error_handler import register_error_handlers
from .helpers import requires_login, requires_admin, do_login, do_logout, CURR_USER_KEY
from . import users_bp, views, auth, idealog, api

def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///idealog')

    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    url = urlparse(os.environ.get('REDISCLOUD_URL', 'redis://localhost'))
    r = redis.Redis(host=url.hostname, port=url.port, password=url.password)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'devnotcompletelyrandomsecretkey'),
        SQLALCHEMY_DATABASE_URI=DATABASE_URL,
        CELERY=dict(
            broker_url=os.environ.get('REDISCLOUD_URL', 'redis://localhost'),
            result_backend=os.environ.get('REDISCLOUD_URL', 'redis://localhost'),
            task_ignore_result=True,
        ),
    )
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
    app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'development')
    app.config['FLASK_DEBUG'] = os.environ.get('FLASK_DEBUG', True)

    app.config.from_prefixed_env()
    celery_app = celery_init_app(app)

    db.init_app(app)

    #if i wannt to keep app.before_request in a separate file and register it here - how to do it?
    @app.before_request
    def add_user_to_g():
        """If we're logged in, add curr user to Flask global."""
        if CURR_USER_KEY in session:
            g.user = User.query.get(session[CURR_USER_KEY])
        else:
            g.user = None

    @app.after_request
    def add_header(req):
        """Add non-caching headers on every request."""
        req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        req.headers["Pragma"] = "no-cache"
        req.headers["Expires"] = "0"
        req.headers['Cache-Control'] = 'public, max-age=0'
        return req

    register_error_handlers(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(users_bp.bp, url_prefix='/users_bp')
    app.register_blueprint(views.bp)
    app.register_blueprint(idealog.bp)
    app.register_blueprint(api.bp)

    app.add_url_rule('/', endpoint='index')

    return app