from flask import Flask, render_template, make_response, request, g, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' 
db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template('login.html')

# Define a User table schema
class User(db.Model):
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
        password_input = request.form.get('register-password')
        email_input = request.form.get('register-email')
        admin_auth_register(email_input, password_input)
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run()

