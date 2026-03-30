import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app import app, db
from flask import session
from models import User
from werkzeug.security import generate_password_hash

class TestUserLogin(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        # Create the database and add a test user
        with app.app_context():
            db.create_all()
            test_user = User(email='test@email.com', name='John Smith', password=generate_password_hash('correctpassword'))
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login_success(self):
        """
        Test that login is successful and a session token is given to the user
        Asserts that:
            - Response is successful (200)
            - The user is redirected to the dashboard
            - If a success json response is given by the server
            - The session token is given to the user
        """

        response = self.client.post('/login', data={
            'email': 'test@email.com',
            'password': 'correctpassword'
        })
        
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['redirect'], '/dashboard')
        
        with self.client.session_transaction() as sess:
            self.assertIn('_user_id', sess)

    def test_unsuccessful_login(self):
        """
        Test that login is unsuccessful with an unregistered user
        Asserts that:
            - Response is not successful (400)
            - The user is not redirected to the dashboard
            - If a success json response is false
        """
        response = self.client.post('/login', data={
            'email': 'test@email.com',
            'password': 'wrongpassword'
        })
        
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])

if __name__ == '__main__':
    unittest.main()