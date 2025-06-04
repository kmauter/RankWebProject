from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

# Scopes for managing YouTube playlists
SCOPES = ['https://www.googleapis.com/auth/youtube']

def get_youtube_service():
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def create_youtube_playlist(playlist_title, playlist_description, songs):
    youtube = get_youtube_service()
    # 1. Create the playlist
    playlist_request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": playlist_title,
                "description": playlist_description
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    playlist_response = playlist_request.execute()
    playlist_id = playlist_response["id"]

    # 2. For each song, search and add the top result to the playlist
    for song in songs:
        query = f"{song.title} {song.artist}"
        search_response = youtube.search().list(
            q=query,
            part="id",
            maxResults=1,
            type="video"
        ).execute()
        items = search_response.get("items")
        if items:
            video_id = items[0]["id"]["videoId"]
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()
    print(f"YouTube playlist created: https://www.youtube.com/playlist?list={playlist_id}")
    return f"https://www.youtube.com/playlist?list={playlist_id}"