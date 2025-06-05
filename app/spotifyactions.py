import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
from spotipy import Spotify
import requests
from dotenv import load_dotenv
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def get_spotify_access_token_from_refresh(refresh_token):
    # Use the refresh token to get a new access token
    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        print('Failed to refresh Spotify token:', response.text)
        return None
    return response.json().get('access_token')


def get_spotify_user_id(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    if response.status_code != 200:
        print('Failed to get Spotify user id:', response.text)
        return None
    return response.json().get('id')


def create_spotify_playlist_for_game(game, songs, playlist_name, spotify_refresh_token):
    access_token = get_spotify_access_token_from_refresh(spotify_refresh_token)
    if not access_token:
        print('Could not get Spotify access token.')
        return None
    sp = Spotify(auth=access_token)
    user_id = get_spotify_user_id(access_token)
    if not user_id:
        print('Could not get Spotify user id.')
        return None

    # Create a new playlist for the game
    playlist_name = playlist_name or f"Game {game.id} Playlist"
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
    playlist_id = playlist['id']

    # Search and collect track URIs
    track_uris = []
    for song in songs:
        query = f"{song.title} {song.artist}"
        results = sp.search(q=query, type='track', limit=1)
        items = results['tracks']['items']
        if items:
            track_uris.append(items[0]['uri'])

    # Add tracks to the playlist (in batches of 100)
    for i in range(0, len(track_uris), 100):
        sp.playlist_add_items(playlist_id, track_uris[i:i+100])

    print(f"Spotify playlist created for game {game.id}: {playlist['external_urls']['spotify']}")
    return playlist['external_urls']['spotify']