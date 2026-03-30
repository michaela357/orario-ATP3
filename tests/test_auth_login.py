import sys
import os
import pytest
from werkzeug.security import generate_password_hash

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User

@pytest.fixture
def client():
    """
    Fixture to set up a clean test client and in-memory database
    for every single test function.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            valid_test_user = User(
                email='test@email.com', 
                name='John Smith', 
                password=generate_password_hash('Correctpassword123!')
            )
            db.session.add(valid_test_user)
            db.session.commit()
            
            yield client
            
            db.session.remove()
            db.drop_all()

def test_login_success(client):
    """
    Test that login is successful and a session token is given to the user
    Asserts that:
        - Response is successful (200)
        - The user is redirected to the dashboard
        - If a success json response is given by the server
        - The session token is given to the user
    """
    response = client.post('/login', data={
        'email': 'test@email.com',
        'password': 'Correctpassword123!'
    })
    
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['success'] is True
    assert data['redirect'] == '/dashboard'
    
    with client.session_transaction() as sess:
        assert '_user_id' in sess

def test_unsuccessful_login(client):
    """
    Test that login is unsuccessful with an unregistered user
    Asserts that:
        - Response is not successful (400)
        - The user is not redirected to the dashboard
        - If a success json response is false
    """
    response = client.post('/login', data={
        'email': 'unregistered_user@email.com',
        'password': 'NotARealPassword123!'
    })
    
    data = response.get_json()
    
    assert response.status_code == 400
    assert data['success'] is False