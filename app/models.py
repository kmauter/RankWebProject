from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum as PyEnum
from sqlalchemy.types import JSON

class User(db.Model):
    __tablename__ = 'User'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    spotify_refresh_token = db.Column(db.String, nullable=True)
    youtube_refresh_token = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Stage(PyEnum):
    SUBMIT = 'submissions'
    RANK = 'rankings'
    DONE = 'results'    
    
class Game(db.Model):
    __tablename__ = 'Game'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    theme = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    stage = db.Column(db.Enum(Stage), nullable=False)
    submission_duedate = db.Column(db.Date, nullable=False)
    rank_duedate = db.Column(db.Date, nullable=False)
    game_code = db.Column(db.String, nullable=False)
    max_submissions_per_user = db.Column(db.Integer, nullable=False, default=2)
    spotify_playlist_url = db.Column(db.String, nullable=True)
    youtube_playlist_url = db.Column(db.String, nullable=True)
    song_order = db.Column(JSON, nullable=True) 
    
    __table_args__ = (
        db.UniqueConstraint('game_code', name='uq_game_code'),  # Explicitly define the unique constraint name
    )
    
    owner = db.relationship('User', backref='games')  # Link to User

    def __repr__(self):
        return '<Game {}>'.format(self.theme)
    
class GameUser(db.Model):
    __tablename__ = 'GameUser'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('Game.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('game_id', 'user_id', name='uq_game_user'),
    )

    def __repr__(self):
        return '<GameUser {}>'.format(self.id)
    
class Song(db.Model):
    __tablename__ = 'Song'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('Game.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    comment = db.Column(db.String, nullable=True)
    # spotify_link = db.Column(db.String, nullable=True)
    # youtube_link = db.Column(db.String, nullable=True)
    
    # Define relationships here
    user = db.relationship('User', backref='songs')  # Link to User
    game = db.relationship('Game', backref='songs')  # Link to Game
    
    def __repr__(self):
        return '<Song {}>'.format(self.title)
    
class Rank(db.Model):
    __tablename__ = 'Rank'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('Game.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('Song.id'), nullable=False)
    rank_position = db.Column(db.Integer, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('game_id', 'user_id', 'song_id', name='uq_rank'), # -- avoids duplicate ranks for the same song
        db.UniqueConstraint('game_id', 'user_id', 'rank_position', name='uq_rank_position'), # -- one rank per user per position
    )

    def __repr__(self):
        return f'<Rank game={self.game_id} user={self.user_id} song={self.song_id} position={self.rank_position}>'
    
    
class SongStat(db.Model):
    __tablename__ = 'SongStat'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    song_id = db.Column(db.Integer, db.ForeignKey('Song.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('Game.id'), nullable=False)
    
    avg_rank = db.Column(db.Float, nullable=True)
    median_rank = db.Column(db.Float, nullable=True)
    rank_range = db.Column(db.Integer, nullable=True)
    controversy = db.Column(db.Float, nullable=True)
    
    __table_args__ = (
        db.UniqueConstraint('song_id', 'game_id', name='uq_song_game_stat'),
    )
    
    song = db.relationship('Song', backref='stats')
    game = db.relationship('Game', backref='song_stats')
    
    def __repr__(self):
        return f'<SongStat song={self.song_id} game={self.game_id}>'