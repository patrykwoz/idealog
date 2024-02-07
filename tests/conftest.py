import os
import psycopg2
from sqlalchemy import text
import pytest
from idealog import create_app
from idealog.models import db as _db

@pytest.fixture
def app(test_db):
    """Configure and yield a Flask app with a test database."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'postgresql://postgres:postgres@localhost/{test_db}',
        'DATABASE_URL': f'postgresql://postgres:postgres@localhost/{test_db}',
    })

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
    # Create a new test database
    test_db_name = 'idealogtestdb_test'
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='postgres',
        host='localhost'
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    cur.execute(f"CREATE DATABASE {test_db_name}")
    cur.close()
    conn.close()

    # Yield the test database name
    yield test_db_name

    # Drop the test database after ensuring no active connections
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='postgres',
        host='localhost'
    )
    conn.autocommit = True
    cur = conn.cursor()
    # Terminate all other sessions accessing the database
    cur.execute(f"""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE datname = '{test_db_name}' AND pid <> pg_backend_pid()
    """)
    cur.close()

    # Now drop the database
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    cur.close()
    conn.close()

@pytest.fixture
def db_session(test_db):
    """Provide a session for the test database."""
    # Create a connection to the test database
    conn = psycopg2.connect(
        dbname=test_db, 
        user='postgres', 
        password='postgres', 
        host='localhost'
    )
    conn.autocommit = True

    # Create a transaction and session
    transaction = conn.begin()
    Session = sessionmaker(bind=conn)
    session = Session()

    yield session

    # Rollback transaction and close connection
    session.close()
    transaction.rollback()
    conn.close()
