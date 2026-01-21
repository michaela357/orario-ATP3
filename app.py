from flask import Flask, render_template, make_response, request, g, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import secrets


app = Flask(__name__)
login_manager = LoginManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)

db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('home.html')

# Define a User table schema
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=True)

    #constructor method
    def __init__(self, email, password): 
        self.email = email
        self.password = password

# Create the database tables from she
with app.app_context():
    db.create_all()

#Helper function to store new user to database
def admin_auth_register(email_input, password_input):
    new_user = User(email=email_input, password=password_input)
    db.session.add(new_user)
    db.session.commit()

#POST route to register user and GET to load HTML template
@app.route('/register/', methods=['POST', 'GET'])
def user_register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        register_password = request.form.get('register-password')
        register_email = request.form.get('register-email')

        hashed_password = generate_password_hash(register_password)
        username_exists = User.query.filter(User.email == register_email).first()

        if not username_exists:
            admin_auth_register(register_email, hashed_password)

        return redirect(url_for('login'))
    
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, id)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        login_email = request.form['login-email']
        login_password = request.form['login-password']

        correct_user = User.query.filter(User.email == login_email).first()

        if correct_user is not None and check_password_hash(correct_user.password, login_password):
            login_user(correct_user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('home.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

