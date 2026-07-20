from app import db
from models import DailyStudyLog
from datetime import date

def test_save_study_time(client, authenticated_user):
    """
    Tests saving study minutes. Verifies both creating a fresh log 
    and accumulating minutes onto an existing log for the same day.

    Asserts that:
        - Creating a fresh log is saved in the databse
        - Subsequent logs are added to the total
        - Responds with success- 200
    """
    # Save minutes for the first time in the day
    response1 = client.post('/api/save_study_time', json={'minutes': 25})

    assert response1.status_code == 200
    assert response1.get_json()['total_minutes'] == 25

    user_id = authenticated_user.id

    # Verify database entry exists
    today = date.today()
    log = db.session.get(DailyStudyLog, user_id)
    if not log:
        log = DailyStudyLog.query.filter_by(user_id=authenticated_user.id, date=today).first()
        
    assert log.total_minutes == 25

    # Save more minutes on the same day to test accumulation
    response2 = client.post('/api/save_study_time', json={'minutes': 15})
    assert response2.status_code == 200

    # Check total minutes are 15+25 = 40
    assert response2.get_json()['total_minutes'] == 40