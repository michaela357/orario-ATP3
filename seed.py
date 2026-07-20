from datetime import date, timedelta
from app import app, db
from models import User, Task, DailyStudyLog
from werkzeug.security import generate_password_hash

with app.app_context():
    print("Clearing old data...")
    db.drop_all()
    db.create_all()

    print("Seeding database...")

    # Create the Evaluator User
    evaluator = User(
        name="Mr Test",
        email="teacher@test.com",
        password=generate_password_hash("Password123!"),
        study_group="Seeded study group",
        is_studying=False,
        study_time=0,
        quote="Success is the sum of small efforts repeated day in and day out."
    )
    db.session.add(evaluator)
    db.session.flush()

    # Seed Tasks for the To-Do Statistics Widget
    today = date.today()
    tasks = [
        Task(title="Complete Assessment Write-up", description="Final evaluation paper", due_date=today, is_complete=True, reminder=False, user_id=evaluator.id),
        Task(title="Review Flashcard Deck", description="Study core pipeline steps", due_date=today, is_complete=False, reminder=True, user_id=evaluator.id),
        Task(title="Submit Project Repository", description="Push final codebase", due_date=today + timedelta(days=1), is_complete=False, reminder=False, user_id=evaluator.id),
        Task(title="Overdue Research Notes", description="From last week", due_date=today - timedelta(days=4), is_complete=False, reminder=False, user_id=evaluator.id)
    ]
    db.session.add_all(tasks)

    # Seed a 5-Day Study Streak
    logs = []
    for i in range(5):
        logs.append(
            DailyStudyLog(
                user_id=evaluator.id,
                date=today - timedelta(days=i),
                study_group="Seeded study group",
                total_minutes=45 + (i * 5)
            )
        )
    db.session.add_all(logs)

    # Add a dummy user to the same group to show the leaderboard functionality
    peer_user = User(
        name="Alex Smith",
        email="alex@test.com",
        password=generate_password_hash("Password123!"),
        study_group="Seeded study group",
        study_time=20,
        is_studying=True  # This user will display the active pulsing green dot
    )

    peer_user_2 = User(
        name="John Poulos",
        email="jp@test.com",
        password=generate_password_hash("Password123!"),
        study_group="Seeded study group",
        study_time=2,
        is_studying=False
    )

    db.session.add(peer_user)
    db.session.add(peer_user_2)
    db.session.flush()

    peer_log = DailyStudyLog(
        user_id=peer_user.id,
        date=today,
        study_group="Seeded study group",
        total_minutes=30
    )
    db.session.add(peer_log)

    peer_2_log = DailyStudyLog(
        user_id=peer_user_2.id,
        date=today,
        study_group="Seeded study group",
        total_minutes=30
    )
    db.session.add(peer_2_log)

    db.session.commit()
    print("Database successfully seeded! Ready for evaluation.")