from app import app, db
from app.models import User
from flask import request
from flask import jsonify
import datetime
import jwt
from app.config import SECRET_KEY

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
        # Generate a JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
            },
            SECRET_KEY,
            algorithm='HS256'
        )
        return jsonify({'message': 'Login successful!', 'token': token, 'user_id': user.id})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
    
@app.route('/api/user-profile', methods=['GET'])
def get_user_profile():
    token = request.headers.get('Authorization').split(" ")[1]  # Extract token from "Bearer <token>"
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(decoded['user_id'])
        if not user:
            return jsonify({'message': 'User not found'}), 404
        return jsonify({'username': user.username, 'email': user.email})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'message': 'Invalid token'}), 401