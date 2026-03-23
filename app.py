from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import html
import regex as re
from datetime import timedelta

from extensions import db

# Initialise Flask app
app = Flask(__name__)
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

        sanitised_name = html.escape(cleaned_name) # in case any HTML tags remain, escape them

        if not re.match(r"^[a-zA-Z0-9+!+#]+(?:[._-][a-zA-Z0-9+!+#]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$", email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        if email == "":
            return jsonify({'success': False, 'error': 'Must enter an email!'}), 400

        if len(password) < 8 or len(password) > 64:
            return jsonify({'success': False, 'error': 'Password too short'}), 400
        
        elif re.search(r"[a-z]", password) == None:
            return jsonify({'success': False, 'error': 'Password does not meet requirements'}), 400
        
        elif re.search(r"[A-Z]", password) == None:
            return jsonify({'success': False, 'error': 'Password must contain a capital letter'}), 400
        
        elif re.search(r"[0-9]", password) == None:
            return jsonify({'success': False, 'error': 'Password must contain a digit'}), 400
        
        elif re.search(r"[!@#$%^&*]", password) == None:
            return jsonify({'success': False, 'error': 'Password must contain a special character'}), 400

        sanitised_name = html.escape(cleaned_name)
        name_parts = sanitised_name.split()
        first_name = name_parts[0] if name_parts else "User"

        # Implement try / except to catch any database errors
        try:
            new_user = User(email=email, name=first_name.capitalize(), password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"success": True, "redirect": "/login"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": "Database error"}), 500

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
    return render_template('dashboard.html', name=current_user.name)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

