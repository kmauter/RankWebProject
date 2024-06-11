from app import app, db
from app.models import User
from flask import request

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/register', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']  # This should be hashed
    password2 = data['password2'] 

    if password != password2:
        return 'Passwords do not match'

    # Check if user already exists
    user = User.query.filter_by(username=username).first()

    if user:
        return 'User already exists'
    
    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return 'User added'

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']  # This should be hashed

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        return 'Login successful!'
    else:
        return 'Invalid username or password'