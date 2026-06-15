import os
import sys

import pytest
import regex as re
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
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    
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


def test_csrf_token_exists_on_register_page(client):
    """
    Tests that the hidden input field exists on the registration page
    Asserts that:
        - The response is 200 OK, as intended
        - There is a CSRF token in the HTML
        - The CSRF token is hidden
    """
    response = client.get("/register/")
    assert response.status_code == 200
    
    html_content = response.data.decode()
    assert 'name="csrf_token"' in html_content
    assert 'type="hidden"' in html_content

def test_csrf_token_exists_on_login_page(client):
    """
    Tests that the hidden input field exists on the login page
    Asserts that:
        - The response is 200 OK, as intended
        - There is a CSRF token in the HTML
        - The CSRF token is hidden
    """
    response = client.get("/login")
    assert response.status_code == 200
    
    html_content = response.data.decode()
    assert 'name="csrf_token"' in html_content
    assert 'type="hidden"' in html_content

def test_csrf_token_different_between_sessions():
    """
    Test that each session generates a unique CSRF token
    Asserts that:
        - The number of unique elements in the tokens list is the same 
          as the length of the list (i.e. all generated tokens are unique)
    """
    tokens = []

    for _ in range(3):
        with app.test_client() as client:
            response = client.get("/register/")
            html = response.data.decode()

            token = re.search(r'name="csrf_token" value="(.+?)"', html).group(1)

            tokens.append(token)

    assert len(tokens) == len(set(tokens))


def test_invalid_csrf_token(client):
    """
    Tests that an request with an invalid CSRF token does not work
    Asserts that:
        - A request with an invalid CSRF token is rejected with a 400 error
        - The type of error is "CSRF Error"
    """
    response = client.post('/register/', 
        headers={"X-CSRFToken": 'this_is_a_fake_token'},
        data={
            'email': 'test2@email.com.au',
            'name' : 'John Smith',
            'password' : 'Password1!'
        }
    )


    assert response.status_code == 400
    html_content = response.data.decode('utf-8')
    assert "csrf" in html_content.lower() or "token" in html_content.lower()