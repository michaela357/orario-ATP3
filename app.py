from flask import Flask, render_template, make_response, request, g, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' 
db = SQLAlchemy(app)

# Define a User table schema
class User(db.Model):
    name = db.Column('name', db.String(100), primary_key=True)
    email = db.Column('email', db.String(100), nullable=False, unique=True)
    password = db.Column('password', db.String(200), nullable=True)

    #constructor method
    def __init__(self, name, email, password): 
        self.user_id = name
        self.email = email
        self.password = password

    #set and get methods
    def get_id(self):
        return self.name
    
    def get_email(self):
        return self.email
    

# Create the database tables from she
with app.app_context():
    db.create_all()

#Helper function to store new user to database
def admin_auth_register(name_input, email_input, password_input):
    new_user = User(name=name_input, email=email_input, password=password_input)
    db.session.add(new_user)
    db.session.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template('register.html')

if __name__ == "__main__":
    app.run()

