import spotipy
from spotipy.oauth2 import SpotifyOAuth

def create_spotify_playlist_for_game(game, songs, user_spotify_id, playlist_name=None):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        redirect_uri="YOUR_REDIRECT_URI",
        scope="playlist-modify-public playlist-modify-private"
    ))

    # Create a new playlist for the game
    playlist_name = playlist_name or f"Game {game.id} Playlist"
    playlist = sp.user_playlist_create(user_spotify_id, playlist_name, public=False)
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