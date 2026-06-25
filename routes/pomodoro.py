import html
from datetime import datetime

from flask import Blueprint, jsonify, request, url_for
from flask_login import current_user, login_required

from extensions import db

pomodoro_bp = Blueprint("pomodoro", __name__)