import os
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    session,
    g,
    send_file,
)
from celery.result import AsyncResult

from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy import func

from .celery_app import celery_init_app

from .forms import (
    UserAddForm,
    UserSignupForm,
    LoginForm,
    UserEditForm,
    IdeaAddForm,
    GroupAddForm,
    KnowledgeSourceAddForm,
    KnowledgeDomainAddForm,
    KnowledgeBaseAddForm,
    KnowledgeBaseEditForm,
)

from .models import (
    db,
    connect_db,
    User,
    Idea,
    Group,
    KnowledgeSource,
    KnowledgeDomain,
    KnowledgeBase,
)

from . import users, views, auth, error_handlers, file_handlers, idealog, api

def create_app(test_config=None) -> Flask:
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Fetch the DATABASE_URL from the environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///idealog')

    # Check if the URL needs to be modified for SQLAlchemy compatibility
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    url = urlparse(os.environ.get('REDISCLOUD_URL', 'redis://localhost'))
    r = redis.Redis(host=url.hostname, port=url.port, password=url.password)

    # Set SECRET_KEY and DATABASE URL from environment variables with fallback values
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

    app.config.from_prefixed_env()
    celery_app = celery_init_app(app)

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(error_handlers.bp)
    app.register_blueprint(file_handlers.bp)
    app.register_blueprint(views.bp)
    app.register_blueprint(idealog.bp)
    app.register_blueprint(api.bp)

    app.add_url_rule('/', endpoint='index')

    return app