import os
import sys
import pytest
from werkzeug.security import generate_password_hash

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db
from models import User, Flashcard

@pytest.fixture
def client():
    """
    Global fixture to set up a clean test client and in-memory database
    for every single test function.
    """
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            db.create_all()
            
            # Seed the database with default test user
            valid_test_user = User(
                email='test@email.com.au', 
                name='John Smith', 
                password=generate_password_hash('Correctpassword123!'),
                quote='Example quote'
            )
            db.session.add(valid_test_user)
            db.session.commit()
            
            yield test_client
            
            db.session.remove()
            db.drop_all()