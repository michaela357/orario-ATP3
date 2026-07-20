import os
import sys
import pytest
from werkzeug.security import generate_password_hash

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as _app, db as _db
from models import User


@pytest.fixture(scope='function')
def app():
    """
    Create a fresh app instance for each test with isolated configuration.
    This prevents tests from affecting the production database.
    """
    # Store original config
    original_config = _app.config.copy()

    # Configure for testing
    _app.config['TESTING'] = True
    _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    _app.config['WTF_CSRF_ENABLED'] = False
    _app.config['SERVER_NAME'] = 'localhost'

    # Create application context
    with _app.app_context():
        _db.create_all()
        yield _app

        # Cleanup
        _db.session.remove()
        _db.drop_all()

    # Restore original config (important!)
    _app.config.update(original_config)


@pytest.fixture(scope='function')
def db(app):
    """
    Provide the database instance with test app context.
    """
    return _db

@pytest.fixture(scope='function')
def authenticated_user(db):
    """
    Create a test user that can be used for authentication tests.
    """
    user = User(
        email='test@email.com.au',
        name='John Smith',
        password=generate_password_hash('Correctpassword123!'),
        quote=None,
        study_time=0,
        is_studying=False,
        study_group=''
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture(scope='function')
def client(app, authenticated_user):
    """
    Provide a pre-authenticated test client linked directly to the created user.
    """
    test_client = app.test_client()
    
    # Inject the session cookies Flask-Login expects for authenticated users
    with test_client.session_transaction() as sess:
        sess['_user_id'] = str(authenticated_user.id)
        sess['_fresh'] = True
        
    return test_client


@pytest.fixture(scope='function')
def anon_client(app):
    """
    Provide an unauthenticated client for testing logouts e.t.c.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def csrf_client():
    """
    Provide a test client with CSRF protection enabled for CSRF tests.
    """
    # Store original config
    original_config = _app.config.copy()

    # Configure for CSRF testing
    _app.config['TESTING'] = True
    _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    _app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF for these tests
    _app.config['SESSION_COOKIE_SECURE'] = False
    _app.config['SERVER_NAME'] = 'localhost'

    with _app.test_client() as client:
        with _app.app_context():
            _db.create_all()

            # Create test user for CSRF tests
            user = User(
                email='test@email.com.au',
                name='John Smith',
                password=generate_password_hash('Correctpassword123!'),
                quote=None,
                study_time=0,
                is_studying=False,
                study_group=''
            )
            _db.session.add(user)
            _db.session.commit()

            yield client

            _db.session.remove()
            _db.drop_all()

    # Restore original config
    _app.config.update(original_config)
