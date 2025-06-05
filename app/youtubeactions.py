from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import requests
from dotenv import load_dotenv
load_dotenv()

YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')

# Scopes for managing YouTube playlists
SCOPES = ['https://www.googleapis.com/auth/youtube']

def get_youtube_access_token_from_refresh(refresh_token):
    token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': YOUTUBE_CLIENT_ID,
        'client_secret': YOUTUBE_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        print('Failed to refresh YouTube token:', response.text)
        return None
    return response.json().get('access_token')


def create_youtube_playlist_for_game(game, songs, playlist_name, youtube_refresh_token):
    access_token = get_youtube_access_token_from_refresh(youtube_refresh_token)
    if not access_token:
        print('Could not get YouTube access token.')
        return None
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    # 1. Create the playlist
    playlist_name = playlist_name or f"Game {game.id} Playlist"
    playlist_body = {
        "snippet": {
            "title": playlist_name,
            "description": f"Playlist for game {game.id}"
        },
        "status": {
            "privacyStatus": "private"
        }
    }
    playlist_response = requests.post(
        'https://www.googleapis.com/youtube/v3/playlists?part=snippet%2Cstatus',
        headers=headers,
        json=playlist_body
    )
    if playlist_response.status_code != 200:
        print('Failed to create YouTube playlist:', playlist_response.text)
        return None
    playlist_id = playlist_response.json()["id"]

    # 2. For each song, search and add the top result to the playlist
    for song in songs:
        query = f"{song.title} {song.artist}"
        search_params = {
            'part': 'id',
            'q': query,
            'maxResults': 3,
            'type': 'video',
        }
        search_response = requests.get(
            'https://www.googleapis.com/youtube/v3/search',
            headers={'Authorization': f'Bearer {access_token}'},
            params=search_params
        )
        if search_response.status_code != 200:
            print(f"Failed to search for song '{query}':", search_response.text)
            continue
        items = search_response.json().get("items")
        if items:
            video_id = None
            for item in items:
                if item["id"]["kind"] == "youtube#video":
                    video_id = item["id"]["videoId"]
                    break
            if not video_id:
                print(f"No video found for song '{query}'. Skipping.")
                continue
            
            add_body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
            add_response = requests.post(
                'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet',
                headers=headers,
                json=add_body
            )
            if add_response.status_code != 200:
                print(f"Failed to add video {video_id} to playlist:", add_response.text)
    print(f"YouTube playlist created for game {game.id}: https://www.youtube.com/playlist?list={playlist_id}")
    return f"https://www.youtube.com/playlist?list={playlist_id}"