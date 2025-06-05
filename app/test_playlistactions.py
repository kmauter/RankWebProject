from app.spotifyactions import create_spotify_playlist_for_game
from app.youtubeactions import create_youtube_playlist_for_game

class MockSong:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist

class MockGame:
    def __init__(self, id, theme):
        self.id = id
        self.theme = theme
        
SPOTIFY_REFRESH_TOKEN = "..."
YOUTUBE_REFRESH_TOKEN = "..."

def test_create_playlist():
    game = MockGame(id=123, theme="Test Playlist")
    songs = [
        MockSong("Imagine", "John Lennon"),
        MockSong("Hey Jude", "The Beatles"),
    ]
    url = create_spotify_playlist_for_game(game, songs, "Test Playlist", SPOTIFY_REFRESH_TOKEN)
    print("Created playlist URL:", url)

if __name__ == "__main__":
    test_create_playlist()