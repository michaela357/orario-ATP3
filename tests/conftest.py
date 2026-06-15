import os
import sys
import pytest
from werkzeug.security import generate_password_hash
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db
from models import User, Task, Flashcard

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

            valid_tasks = Task(
                title="To-do task title",
                description="Description for a valid task",
                due_date=datetime.strptime('5/5/2019','%d/%m/%Y'),
                reminder=True,
                is_complete=True,
                user_id=1
            )

            valid_flashcard = Flashcard(
                user_id=1,
                front="The front of a valid flashcard",
                back="The back of a valid flashcard",
                group="A unique flashcard group",
            )

            db.session.add(valid_test_user)
            db.session.add(valid_tasks)
            db.session.add(valid_flashcard)
            db.session.commit()
            
            yield test_client
            
            db.session.remove()
            db.drop_all()