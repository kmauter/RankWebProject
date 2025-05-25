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
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/games', methods=['POST'])
def create_game():
    token = request.headers.get('Authorization').split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = decoded['user_id']
    
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

        if not user_id:
            return jsonify({'error': 'User not found'}), 404

        # Create the game
        new_game = Game(
            theme=theme,
            stage=Stage.SUBMIT,
            submission_duedate=submission_duedate,
            rank_duedate=rank_duedate,
            game_code=game_code,
            owner_id=user_id
        )
        db.session.add(new_game)
        db.session.commit()

        # Add the user to the game
        game_user = GameUser(game_id=new_game.id, user_id=user_id)
        db.session.add(game_user)
        db.session.commit()

        return jsonify({
            'message': 'Game created successfully',
            'game_code': game_code,
        }), 201
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/join-game', methods=['POST'])
def join_game():
    token = request.headers.get('Authorization').split(" ")[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = decoded['user_id']
        
        data = request.get_json()
        game_code = data.get('game_code')
        
        if not game_code:
            return jsonify({'error': 'Missing game code'}), 400
        
        # Find the game by game code
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        # Check if the user is already part of the game
        existing_entry = GameUser.query.filter_by(game_id=game.id, user_id=user_id).first()
        if existing_entry:
            return jsonify({'error': 'User already part of the game'}), 400
        
        # Add the user to the game
        game_user = GameUser(game_id=game.id, user_id=user_id)
        db.session.add(game_user)
        
        db.session.commit()
        return jsonify({'message': 'User added to game successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
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
                'dueDate': game.rank_duedate.strftime('%Y-%m-%d'),  # Format date as string
                'gameCode': game.game_code
            }
            for game in games
        ]

        return jsonify(game_data), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/submit-song', methods=["POST"])
def submit_song_to_game():
    token = request.headers.get('Authorization').split(" ")[1] # Extract token from "Bearer <token>"
    try:
        # Decode the JWT token to get the user ID
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = decoded['user_id']
        
        data = request.get_json()
        game_code = data.get('game_code')
        title = data.get('song_name')
        artist = data.get('artist')
        comment = data.get('comment')
        
        if not game_code or not title or not artist:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find the game by game code
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        # Check if the game is in the submission stage
        if game.stage != Stage.SUBMIT:
            return jsonify({'error': 'Game is not in the submission stage'}), 400
        
        # Check if the user is part of the game
        game_user = GameUser.query.filter_by(game_id=game.id, user_id=user_id).first()
        if not game_user:
            return jsonify({'error': 'User is not part of the game'}), 403
        
        # Check if the song already exists for this game
        existing_song = Song.query.filter_by(game_id=game.id, user_id=user_id, title=title, artist=artist).first()
        if existing_song:
            return jsonify({'error': 'Song already submitted for this game'}), 400
        
        # Create a new song entry
        song_entry = Song(
            game_id=game.id,
            user_id=user_id,
            title=title,
            artist=artist,
            comment=comment
        )
        db.session.add(song_entry)
        db.session.commit()
        # return the song entry
        return jsonify({
            'message': 'Song submitted successfully',
            'song': {
                'id': song_entry.id,
                'song_name': song_entry.title,
                'artist': song_entry.artist,
                'comment': song_entry.comment
            }
        }), 201
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/game-songs', methods=["GET"])
def get_game_songs():
    token = request.headers.get('Authorization').split(" ")[1]
    try:
        # Decode the JWT token to get the user ID
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = decoded['user_id']
        
        data = request.get_json()
        game_code = data.get('game_code')
        
        if not game_code:
            return jsonify({'error': 'Missing game code'}), 400
        
        # Find the game by game code
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        # Check if the user is part of the game
        game_user = GameUser.query.filter_by(game_id=game.id, user_id=user_id).first()
        if not game_user:
            return jsonify({'error': 'User is not part of the game'}), 403
        
        # Get all songs for this game
        songs = Song.query.filter_by(game_id=game.id).all()
        
        # Serialize the song data
        song_data = [
            {
                'id': song.id,
                'song_name': song.title,
                'artist': song.artist,
                'comment': song.comment,
                'spotify_link': song.spotify_link,
                'youtube_link': song.youtube_link
            }
            for song in songs
        ]
        
        return jsonify(song_data), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401