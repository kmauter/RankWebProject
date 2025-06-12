from app import app, db
from app.models import User, Game, GameUser, Song, Rank, Stage
from flask import request, redirect, url_for, session
from flask import jsonify
from datetime import datetime, timedelta
import os
import jwt
import random
import string
import requests
from app.config import Config
from dotenv import load_dotenv
from urllib.parse import urlencode
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_SCOPES = 'playlist-modify-public playlist-modify-private'

YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REDIRECT_URI = os.environ.get("YOUTUBE_REDIRECT_URI")
YOUTUBE_SCOPES = "https://www.googleapis.com/auth/youtube"

def get_user_id_from_token():
    token = request.headers.get('Authorization').split(" ")[1]
    decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
    return decoded['user_id']

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
            Config.SECRET_KEY,
            algorithm='HS256'
        )
        return jsonify({'message': 'Login successful!', 'token': token, 'user_id': user.id})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
    
@app.route('/api/user-profile', methods=['GET'])
def get_user_profile():
    try:
        user_id = get_user_id_from_token()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        return jsonify({'username': user.username, 'email': user.email})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/games', methods=['POST'])
def create_game():
    try:
        user_id = get_user_id_from_token()
    
        data = request.get_json()
        theme = data.get('theme')
        submission_duedate = data.get('submissionDuedate')
        rank_duedate = data.get('rankDuedate')
        max_submissions_per_user = data.get('maxSubmissionsPerUser', 2)

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
            owner_id=user_id,
            max_submissions_per_user=2  # Default value, can be changed later
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
    try:
        user_id = get_user_id_from_token()
        
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
    try:
        user_id = get_user_id_from_token()

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
                'submissionDueDate': game.submission_duedate.strftime('%Y-%m-%d'),  # Format date as string
                'rankDueDate': game.rank_duedate.strftime('%Y-%m-%d'),  # Format date as string
                'gameCode': game.game_code,
                'maxSubmissionsPerUser': game.max_submissions_per_user,
                'owner': {
                    'id': game.owner_id,
                    'username': (User.query.get(game.owner_id).username if (game.owner_id and User.query.get(game.owner_id)) else None)
                },
                'spotifyPlaylistUrl': game.spotify_playlist_url,
                'youtubePlaylistUrl': game.youtube_playlist_url
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
    try:
        user_id = get_user_id_from_token()
        
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
        
        # Count user's submissions for this game
        user_song_count = Song.query.filter_by(game_id=game.id, user_id=user_id).count()
        if user_song_count >= game.max_submissions_per_user:
            return jsonify({'error': f'Maximum of {game.max_submissions_per_user} submission(s) reached for this game.'}), 400
        
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
    
@app.route('/api/my-game-songs', methods=["GET"])
def get_my_songs_for_game():
    try:
        user_id = get_user_id_from_token()
        
        game_code = request.args.get('game_code')
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
        
        # Get all songs submitted by the user for this game
        songs = Song.query.filter_by(game_id=game.id, user_id=user_id).all()
        
        song_data = [
            {
                'id': song.id,
                'song_name': song.title,
                'artist': song.artist,
                'comment': song.comment
            }
            for song in songs
        ]
        
        return jsonify(song_data), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/game/<game_code>/update-game', methods=["PATCH"])
def update_game(game_code):
    try: 
        user_id = get_user_id_from_token()
        data = request.get_json()
        
        new_submission_duedate = data.get('submissionDuedate')
        new_rank_duedate = data.get('rankDuedate')
        
        if not new_submission_duedate and not new_rank_duedate:
            return jsonify({'error': 'Nothing to update.'}), 400
        
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        if game.owner_id != user_id:
            return jsonify({'error': 'Only the game owner can update the game.'}), 403
        
        if new_submission_duedate:
            game.submission_duedate = datetime.strptime(new_submission_duedate, '%Y-%m-%d').date()
            
        if new_rank_duedate:
            game.rank_duedate = datetime.strptime(new_rank_duedate, '%Y-%m-%d').date()
        db.session.commit()
        return jsonify({'message': 'Game updated successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/game/<game_code>', methods=["GET"])
def get_game_details(game_code):
    try:
        user_id = get_user_id_from_token()
        
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        # Check if the user is part of the game
        game_user = GameUser.query.filter_by(game_id=game.id, user_id=user_id).first()
        if not game_user:
            return jsonify({'error': 'User is not part of the game'}), 403
        
        # Serialize the game data
        game_data = {
            'id': game.id,
            'title': game.theme,
            'status': game.stage.value,  # Convert Enum to string
            'submissionDueDate': game.submission_duedate.strftime('%Y-%m-%d'),  # Format date as string
            'rankDueDate': game.rank_duedate.strftime('%Y-%m-%d'),  # Format date as string
            'gameCode': game.game_code,
            'owner': {
                'id': game.owner_id,
                'username': User.query.get(game.owner_id).username if game.owner_id else None
            },
            'maxSubmissionsPerUser': game.max_submissions_per_user,
            'spotifyPlaylistUrl': game.spotify_playlist_url,
            'youtubePlaylistUrl': game.youtube_playlist_url
        }
        
        return jsonify(game_data), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/game/<game_code>/songs', methods=["GET"])
def get_game_songs_details(game_code):
    try:
        user_id = get_user_id_from_token()
        
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
                'user': {
                    'id': song.user_id,
                    'username': User.query.get(song.user_id).username if song.user_id else None
                }
            }
            for song in songs
        ]
        
        return jsonify(song_data), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/song/<int:song_id>', methods=["DELETE"])
def delete_song(song_id):
    try:
        user_id = get_user_id_from_token()
        song = Song.query.get(song_id)
        if not song:
            return jsonify({'error': 'Song not found'}), 404
        
        game = Game.query.get(song.game_id)
        if not game or game.owner_id != user_id:
            return jsonify({'error': 'Only the game owner can delete songs.'}), 403
        
        db.session.delete(song)
        db.session.commit()
        return jsonify({'message': 'Song deleted successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/game/<game_code>/players', methods=['GET'])
def get_game_players(game_code):
    try:
        user_id = get_user_id_from_token()
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        game_user = GameUser.query.filter_by(game_id=game.id, user_id=user_id).first()
        if not game_user:
            return jsonify({'error': 'User is not part of the game'}), 403
        
        players = GameUser.query.filter_by(game_id=game.id).all()
        player_data = [
            {
                'id': player.user_id,
                'username': User.query.get(player.user_id).username if player.user_id else None
            }
            for player in players
        ]
        return jsonify(player_data), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/game/<game_code>/player/<int:remove_user_id>', methods=['DELETE'])
def remove_player_from_game(game_code, remove_user_id):
    try:
        user_id = get_user_id_from_token()
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        if game.owner_id != user_id:
            return jsonify({'error': 'Only the game owner can remove players.'}), 403
        
        game_user = GameUser.query.filter_by(game_id=game.id, user_id=remove_user_id).first()
        if not game_user:
            return jsonify({'error': 'Player not found in this game'}), 404
        
        db.session.delete(game_user)
        db.session.commit()
        
        return jsonify({'message': 'Player removed successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401
    
@app.route('/api/connect-spotify', methods=['GET'])
def connect_spotify():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    # Use OAuth2 state parameter to pass user_id
    state = str(user_id)
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPES,
        "state": state,
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode(params)
    print("Spotify auth_url:", auth_url)
    return redirect(auth_url)

@app.route('/api/spotifycallback')
def spotify_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code or not state:
        return "Missing code or user", 400
    user_id = state
    # Exchange code for tokens
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    print("Spotify token payload:", payload)
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        return "Failed to get token", 400
    tokens = response.json()
    refresh_token = tokens.get("refresh_token")
    # Save refresh token to user
    user = User.query.get(user_id)
    if not user:
        return "User not found for this OAuth callback", 400
    user.spotify_refresh_token = refresh_token
    db.session.commit()
    return "Spotify account connected! You can close this window."

@app.route('/api/connect-youtube', methods=['GET'])
def connect_youtube():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    state = str(user_id)
    params = {
        "client_id": YOUTUBE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": YOUTUBE_REDIRECT_URI,
        "scope": YOUTUBE_SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    print("YouTube auth_url:", auth_url)
    return redirect(auth_url)

@app.route('/api/youtubecallback')
def youtube_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code or not state:
        return "Missing code or user", 400
    user_id = state
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": YOUTUBE_REDIRECT_URI,
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        return "Failed to get token", 400
    tokens = response.json()
    refresh_token = tokens.get("refresh_token")
    user = User.query.get(user_id)
    user.youtube_refresh_token = refresh_token
    db.session.commit()
    return "YouTube account connected! You can close this window."

@app.route('/api/game/<game_code>/rankings', methods=['GET'])
def get_user_rankings(game_code):
    """Get the current user's rankings for all songs in the game."""
    try:
        user_id = get_user_id_from_token()
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        # Get all ranks for this user and game, ordered by rank_position
        ranks = Rank.query.filter_by(game_id=game.id, user_id=user_id).order_by(Rank.rank_position).all()
        
        ranking = []
        for rank in ranks:
            index = rank.rank_position - 1
            while len(ranking) <= index:
                ranking.append(None)
            ranking[index] = rank.song_id
        
        return jsonify({'ranking': ranking}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401

@app.route('/api/game/<game_code>/rankings', methods=['POST'])
def save_user_rankings(game_code):
    """Save or update the user's rankings for all songs in the game."""
    try:
        user_id = get_user_id_from_token()
        data = request.get_json()
        rank_order = data.get('ranking')  # List of song IDs in ranked order
        if not isinstance(rank_order, list) or not rank_order:
            return jsonify({'error': 'rank_order must be a non-empty list of song IDs'}), 400
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        # Remove any existing ranks for this user/game
        Rank.query.filter_by(game_id=game.id, user_id=user_id).delete()
        # Add new ranks
        print(rank_order)
        for pos, song_id in enumerate(rank_order, start=1):
            print(pos, song_id)
            if song_id is None: continue
            rank = Rank(game_id=game.id, user_id=user_id, song_id=song_id, rank_position=pos)
            db.session.add(rank)
        db.session.commit()
        return jsonify({'message': 'Rankings saved successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401

@app.route('/api/game/<game_code>/rankings', methods=['PATCH'])
def patch_user_rankings(game_code):
    """Partially update the user's rankings for a game (e.g., update a single song's rank)."""
    try:
        user_id = get_user_id_from_token()
        data = request.get_json()
        updates = data.get('updates')  # List of {song_id, rank_position}
        if not isinstance(updates, list) or not updates:
            return jsonify({'error': 'updates must be a non-empty list of objects'}), 400
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        # Use a temporary negative value for rank_position to avoid NOT NULL constraint error
        song_ids = [u.get('song_id') for u in updates if u.get('song_id')]
        ranks_to_update = Rank.query.filter(Rank.game_id==game.id, Rank.user_id==user_id, Rank.song_id.in_(song_ids)).all()
        for idx, rank in enumerate(ranks_to_update):
            rank.rank_position = -1000 - idx  # Use a unique negative value
        db.session.flush()  # Apply changes but don't commit yet
        # Now, set the new rank_position values
        for update in updates:
            song_id = update.get('song_id')
            rank_position = update.get('rank_position')
            if not song_id or not isinstance(rank_position, int):
                continue  # skip invalid
            rank = Rank.query.filter_by(game_id=game.id, user_id=user_id, song_id=song_id).first()
            if rank:
                rank.rank_position = rank_position
            else:
                db.session.add(Rank(game_id=game.id, user_id=user_id, song_id=song_id, rank_position=rank_position))
        db.session.commit()
        return jsonify({'message': 'Rankings updated successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401

@app.route('/api/game/<game_code>/rankings', methods=['DELETE'])
def delete_user_rankings(game_code):
    """Delete all rankings for the current user in the given game."""
    try:
        user_id = get_user_id_from_token()
        game = Game.query.filter_by(game_code=game_code).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        Rank.query.filter_by(game_id=game.id, user_id=user_id).delete()
        db.session.commit()
        return jsonify({'message': 'Rankings deleted successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except Exception as e:
        return jsonify({'error': f'{e}'}), 401