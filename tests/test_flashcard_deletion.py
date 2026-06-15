from app import app
from models import Flashcard

def test_successful_deletion(client):
    """
    Tests that passing a valid target deck identifier to the deletion endpoint
    purges the entries from the database completely.

    Asserts that:
        - A group of flashcards is successfully deleted
        - No flashcards with the group name remain in the database
    """

    with client.session_transaction() as sess:
        sess['_user_id'] = 1

    response = client.post('/delete-group/a-unique-flashcard-group')

    assert response.status_code in [200, 302]
    
    with app.app_context():
        flashcard = Flashcard.query.filter_by(group='a-unique-flashcard-group').first()
        assert flashcard is None