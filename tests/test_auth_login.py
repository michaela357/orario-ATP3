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
        self.app = app.test_client()
        self.app.testing = True

        # Create the database and add a test user
        with app.app_context():
            db.create_all()
            test_user = User(email='meinna@kings.edu.au')
            test_user.set_password('correctpassword')  # Hash and set the password
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == '__main__':
    unittest.main()