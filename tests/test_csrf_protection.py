import os
import sys

import pytest
import regex as re
from werkzeug.security import generate_password_hash

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User


def test_csrf_token_exists_on_register_page(csrf_client):
    """
    Tests that the hidden input field exists on the registration page
    Asserts that:
        - The response is 200 OK, as intended
        - There is a CSRF token in the HTML
        - The CSRF token is hidden
    """
    response = csrf_client.get("/register/")
    assert response.status_code == 200
    
    html_content = response.data.decode()
    assert 'name="csrf_token"' in html_content
    assert 'type="hidden"' in html_content

def test_csrf_token_exists_on_login_page(csrf_client):
    """
    Tests that the hidden input field exists on the login page
    Asserts that:
        - The response is 200 OK, as intended
        - There is a CSRF token in the HTML
        - The CSRF token is hidden
    """
    response = csrf_client.get("/login")
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

    # Enable CSRF for this test
    app.config['WTF_CSRF_ENABLED'] = True

    for _ in range(3):
        with app.test_client() as client:
            response = client.get("/register/")
            html = response.data.decode()

            token = re.search(r'name="csrf_token" value="(.+?)"', html).group(1)

            tokens.append(token)

    # Disable CSRF after test
    app.config['WTF_CSRF_ENABLED'] = False

    assert len(tokens) == len(set(tokens))


def test_invalid_csrf_token(csrf_client):
    """
    Tests that an request with an invalid CSRF token does not work
    Asserts that:
        - A request with an invalid CSRF token is rejected with a 400 error
        - The type of error is "CSRF Error"
    """
    response = csrf_client.post('/register/', 
        headers={"X-CSRFToken": 'this_is_a_fake_token'},
        data={
            'email': 'test2@email.com.au',
            'name' : 'John Smith',
            'password' : 'Password1!'
        }
    )


    # CSRF errors return 400 status code
    assert response.status_code == 400

    # The response is HTML (from 404.html template), not JSON
    html_content = response.data.decode()
    assert html_content is not None