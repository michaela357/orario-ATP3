from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, session, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import html
import regex as re
from datetime import timedelta, datetime
import calendar
from extensions import db

# Initialise Flask app
app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)    # generates a random cryptographically secure key
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Initialise database
db.init_app(app)

# Configure Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Stops circular import
from models import User

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create the database tables
with app.app_context():
    db.create_all()

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Custom error response
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({"success": False, "error": f"CSRF Error: {e.description}"}), 400

@app.errorhandler(404)
def page_not_found_error(e):
    return render_template("404.html", error_message=e.description), 404

# Register route
@app.route('/register/', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = html.escape(request.form.get('name'))
        email = html.escape(request.form.get('email'))
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            return jsonify({'success': False, 'error': 'Email address already exists'}), 400

        
        cleaned_name = name.lower().replace('\x00', '')

        # Use regex to remove any potential dangerous substrings
        dangerous_patterns = [r'onload', 
                            r'onerror', 
                            r'onclick', 
                            r'onmouseover', 
                            r'onfocus', 
                            r'javascript:', 
                            r'data:', 
                            r'<script>', 
                            r'</script>', 
                            r'style',]
        
        # Replace dangerous substrings with an empty string, case insensitive
        for pattern in dangerous_patterns:
            cleaned_name = re.sub(pattern, '', cleaned_name)

        if not email:
            return jsonify({'success': False, 'error': 'Must enter an email!'}), 400
        if not re.match(r"^[a-zA-Z0-9+!+#]+(?:[._-][a-zA-Z0-9+!+#]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$", email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400

        if not password:
            return jsonify({'success': False, 'error': 'Password is required'}), 400

        if len(password) < 8 or len(password) > 64:
            return jsonify({'success': False, 'error': 'Password incorrect length'}), 400
        
        elif re.search(r"[a-z]", password) == None:
            return jsonify({'success': False, 'error': 'Password must contain a lowercase letter'}), 400
        
        elif re.search(r"[A-Z]", password) == None:
            return jsonify({'success': False, 'error': 'Password must contain a capital letter'}), 400
        
        elif re.search(r"[0-9]", password) == None:
            return jsonify({'success': False, 'error': 'Password must contain a digit'}), 400
        
        elif re.search(r"[!@#\-_=+.\$%\^&\*]", password) == None:
            return jsonify({'success': False, 'error': 'Password must contain a special character'}), 400

        sanitised_name = html.escape(cleaned_name)
        name_parts = sanitised_name.split()

        final_name = ''

        for name in name_parts:
            newname = name.capitalize()
            final_name += newname + ' '

        # Implement try / except to catch any database errors
        try:
            new_user = User(email=email, name=final_name.strip(), password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"success": True, "redirect": "/login"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": "An unexpected error occurred"}), 500

    return render_template("register.html")
    
# Login route
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        existing_user = User.query.filter_by(email=email).first()

        if not existing_user or not check_password_hash(existing_user.password, password):
            return jsonify({'success': False, 'error': 'Invalid login details'}), 400
        
        login_user(existing_user, remember=remember)
        return jsonify({"success": True, "redirect": "/dashboard"}), 200
    
    return render_template("login.html")

@app.route('/dashboard')
@login_required
def dashboard():
    first_name = current_user.name.split()[0]

    try:
        year = int(request.args.get("year", datetime.now().year))
        month = int(request.args.get("month", datetime.now().month))
    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid Arguments"
        }), 400
    
    month_name = calendar.month_name[month]

    cal = calendar.Calendar().monthdayscalendar(year, month)

    if month > 1:
        prev_month = month - 1
        prev_year = year
    else:
        prev_month = 12
        prev_year = year - 1
    
    if month < 12:
        next_month = month + 1
        next_year = year
    else:
        next_month = 1
        next_year = year + 1

    today = datetime.now().day
    current_month = datetime.now().month
    current_year = datetime.now().year

    return render_template('dashboard.html',
                           name=first_name,
                           year=year,
                           month=month,
                           calendar=cal,
                           prev_year=prev_year,
                           prev_month=prev_month,
                           next_year=next_year,
                           next_month=next_month,
                           month_name=month_name,
                           today=today,
                           current_month=current_month,
                           current_year=current_year
                           )

@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    
    response = make_response(jsonify({"success": True, "redirect": "/login"}))
    
    # Remove session token and remember token when user logs out
    response.set_cookie('remember_token', '', expires=0)
    response.set_cookie('session', '', expires=0)

    return response

if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')

