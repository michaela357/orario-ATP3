from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
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
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email address already exists', 'error')
            return render_template('register.html')
        
        new_user = User(email=email, name=name, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Login:', 'success')
        return redirect(url_for("login"))

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
            flash('Invalid login details. Try again', 'error')
            return redirect(url_for('login'))
        
        login_user(existing_user, remember=remember)
        return render_template('dashboard.html', name=current_user.name)
    
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

