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