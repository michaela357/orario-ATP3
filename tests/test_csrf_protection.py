import regex as re
from app import app

def test_csrf_token_exists_on_register_page(client):
    """
    Tests that the hidden input field exists on the registration page
    Asserts that:
        - The response is 200 OK, as intended
        - There is a CSRF token in the HTML
        - The CSRF token is hidden
    """
    app.config['WTF_CSRF_ENABLED'] = True

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
    app.config['WTF_CSRF_ENABLED'] = True

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

    app.config['WTF_CSRF_ENABLED'] = True

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
    app.config['WTF_CSRF_ENABLED'] = True

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