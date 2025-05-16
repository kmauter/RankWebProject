from app import app, db
from app.models import User, Game, GameUser, Song, Rank, Stage
from flask import request
from flask import jsonify
from datetime import datetime, timedelta
import jwt
import random
import string
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
                'exp': datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
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
    
@app.route('/api/games', methods=['POST'])
def create_game():
    data = request.get_json()
    theme = data.get('theme')
    submission_duedate = data.get('submissionDuedate')
    rank_duedate = data.get('rankDuedate')

    if not theme or not submission_duedate or not rank_duedate:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        submission_duedate = datetime.strptime(submission_duedate, '%Y-%m-%d').date()
        rank_duedate = datetime.strptime(rank_duedate, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    # Generate a unique game code
    game_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Get the current user (assuming you have a way to get the logged-in user)
    current_user = User.query.filter_by(id=1).first()  # Replace with actual user retrieval logic

    if not current_user:
        return jsonify({'error': 'User not found'}), 404

    # Create the game
    new_game = Game(
        theme=theme,
        stage=Stage.SUBMIT,
        submission_duedate=submission_duedate,
        rank_duedate=rank_duedate,
        game_code=game_code,
    )
    db.session.add(new_game)
    db.session.commit()

    # Add the user to the game
    game_user = GameUser(game_id=new_game.id, user_id=current_user.id)
    db.session.add(game_user)
    db.session.commit()

    return jsonify({
        'message': 'Game created successfully',
        'game_code': game_code,
    }), 201
    
@app.route('/api/user-games', methods=['GET'])
def get_user_games():
    token = request.headers.get('Authorization').split(" ")[1] # Extract token from "Bearer <token>"
    try:
        # Decode the JWT token to get the user ID
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = decoded['user_id']

        # Query the GameUser table to find games the user is part of
        game_user_entries = GameUser.query.filter_by(user_id=user_id).all()
        game_ids = [entry.game_id for entry in game_user_entries]

        # Query the Game table to get details of the games
        games = Game.query.filter(Game.id.in_(game_ids)).all()

        # Serialize the game data
        game_data = [
            {
                'id': game.id,
                'title': game.theme,
                'status': game.stage.value,  # Convert Enum to string
                'dueDate': game.rank_duedate.strftime('%Y-%m-%d')  # Format date as string
            }
            for game in games
        ]

        return jsonify(game_data), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': 'Invalid token'}), 401