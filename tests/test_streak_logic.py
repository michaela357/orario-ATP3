from app import db
from datetime import date, timedelta
from models import DailyStudyLog

def test_streak_logic(client, authenticated_user):
    """
    Tests that the streak engine counts continuous daily logs properly
    and terminates the streak count when a structural gap is hit.
    """
    today = date.today()

    # Seed an artificial 3-day continuous streak directly into the DB context
    log_today = DailyStudyLog(user_id=authenticated_user.id, date=today, total_minutes=30)
    log_yesterday = DailyStudyLog(user_id=authenticated_user.id, date=today - timedelta(days=1), total_minutes=30)
    log_two_days_ago = DailyStudyLog(user_id=authenticated_user.id, date=today - timedelta(days=2), total_minutes=30)
    
    # Add a gap day (3 days ago skipped) and seed an old log to test the loop break condition
    log_five_days_ago = DailyStudyLog(user_id=authenticated_user.id, date=today - timedelta(days=5), total_minutes=30)

    db.session.add_all([log_today, log_yesterday, log_two_days_ago, log_five_days_ago])
    db.session.commit()

    # Call the streak endpoint
    response = client.get('/api/calculate_streak')
    assert response.status_code == 200
    
    # Should evaluate to exactly 3 because day 3 and day 4 were missing
    assert response.get_json()['streak'] == 3