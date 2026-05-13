import sys
import os
import pytest
from flask import session

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_register_success(client):
    """
    Test that registration is successful when valid inputs are entered
    Asserts that:
        - The response returns the correct status code (200)
        - The user is redirected to the login page
    """
    response = client.post('/register/', data={
        'email': 'test@email.com.au',
        'name' : 'John Smith',
        'password' : 'Correctpassword123!'
    })

    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
    assert data['redirect'] == '/login'

    with app.app_context():
        user = User.query.filter_by(email='test@email.com.au').first()
        assert user is not None
        assert user.name == 'John Smith'

def test_unsuccessful_register(client):
    """
    Test that registration fails with a weak password
    Asserts that:
        - Returns a response that indicates an error (400)
        - Check that success is returned as False in the response
        - Make sure that there is no redirect (i.e. unauthorised access)
    """
    response = client.post('/register/', data={
        'email': 'test2@email.com.au',
        'name' : 'John Smith',
        'password' : 'wrongpassword' # Fails Regex
    })

    data = response.get_json()

    assert response.status_code == 400
    assert data['success'] is False
    # Check that it doesn't try to redirect to login
    assert 'redirect' not in data or data['redirect'] != '/login'