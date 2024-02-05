import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, scoped_session
import pytest
from idealog import create_app
from idealog.models import db as _db

@pytest.fixture
def app():
    """Configure and yield a Flask app with a test database."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:postgres@localhost/idealogtestdb',
    })

    _db.init_app(app)

    with app.app_context():
        _db.create_all()

        data_sql_path = os.path.join(os.path.dirname(__file__), 'data.sql')
        with open(data_sql_path, 'rb') as f:
            _data_sql = f.read().decode('utf8')
            _data_sql = text(_data_sql)
            _db.session.execute(_data_sql)
            _db.session.commit()

    yield app

    with app.app_context():
        _db.drop_all()

@pytest.fixture
def client(app):
    """Provide a test client for the application."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Provide a CLI runner for the application."""
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post('/auth/login', data={'username': username, 'password': password})

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    """Provide an authentication helper."""
    return AuthActions(client)

@pytest.fixture
def session(app):
    """Provide a nested transactional session for tests."""
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        options = dict(bind=connection, binds={})
        session = scoped_session(sessionmaker(bind=_db.engine), scopefunc=lambda: options)

        _db.session = session

        yield session

        session.remove()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="module")
def test_db():
    """Fixture to create a test database and dispose of it after testing."""
    engine = create_engine('postgresql://postgres:postgres@localhost/idealogtestdb')
    _db.metadata.create_all(engine)

    yield engine

    _db.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def db_session(test_db):
    """Provide a session for the test database."""
    connection = test_db.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=test_db)
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
