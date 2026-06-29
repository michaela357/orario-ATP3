import html
from datetime import datetime, date
from flask import Blueprint, jsonify, request, url_for, render_template
from flask_login import current_user, login_required

from extensions import db

pomodoro_bp = Blueprint("pomodoro", __name__)

@pomodoro_bp.route("/timer_dashboard", methods=['GET'])
@login_required
def timer_dashboard():
    return render_template('pomodoro.html')

from models import DailyStudyLog


@pomodoro_bp.route('/api/save_study_time', methods=['POST'])
@login_required
def save_study_time():
    data = request.get_json() or {}
    minutes = data.get('minutes')

    if not minutes:
        return jsonify({"success": False, "error": "No time provided"}), 400

    today = date.today()

    try:
        # Check if an entry already exists for this user today
        log = DailyStudyLog.query.filter_by(user_id=current_user.id, date=today).first()

        if log:
            # If it exists, add the new minutes to their current total
            log.total_minutes += int(minutes)
        else:
            # If it's their first session of the day, create a new record
            log = DailyStudyLog(
                user_id=current_user.id,
                date=today,
                total_minutes=int(minutes)
            )
            db.session.add(log)

        db.session.commit()
        return jsonify({"success": True, "total_minutes": log.total_minutes}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500