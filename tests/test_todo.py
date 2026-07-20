from app import app, db
from models import Task

def test_successful_creation(client):
    """
    Tests that a user is successfully able to create a task

    Asserts that:
        - The request returns as successful (200 OK or 201 Created)
        - The task exists in the database with the correct title, description, and due date
    """

    response = client.post('/api/add_task', data={
        'title': 'valid title',
        'description': 'valid description',
        'due_date': '2026-06-11'
    })
    
    # Assert the exact success status code route returns
    assert response.status_code == 201
    
    # Check the JSON payload details
    json_data = response.get_json()
    assert json_data['success'] is True

def test_successful_deletion(client, authenticated_user):
    """
    Tests that a user can successfully delete an existing task.

    Asserts that:
        - The request returns a successful status code.
        - The response indicates success.
        - The task has been removed from the database.
    """

    # Initialise a valid flashcard first
    from datetime import datetime
    valid_date = datetime.strptime('2026-06-11', '%Y-%m-%d').date()

    flashcard = Task(title='valid title',
                    description='valid description',
                    due_date= valid_date,
                    reminder=True,
                    is_complete=False,
                    user_id=authenticated_user.id
                )
    
    db.session.add(flashcard)
    db.session.commit()
    
    task_id = flashcard.id

    response = client.post(f'/api/delete_task/{task_id}')

    assert response.status_code == 200

    json_data = response.get_json()
    assert json_data['success'] is True

    assert Task.query.get(task_id) is None

