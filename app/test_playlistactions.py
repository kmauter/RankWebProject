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
        
SPOTIFY_REFRESH_TOKEN = "AQBehMhluFGnztEn7O4_Udqriyn8sDC9yNNBXsEcXeW3JizS_878N1o_v4pQ1vxO1BnKJq8bSZlq8rQvLq4y4JaPnKqrScs00fcBZHkGfniNcB0equIURSNDU7Lnfnx8CMQ"
YOUTUBE_REFRESH_TOKEN = "1//01Aw4CtEFr6sqCgYIARAAGAESNwF-L9IrxXNdtEUVvoiFzoSfTi8-J42mmgIbPB7eNjYNXoNoOv5ZQE86aPozA2ua1AnIT8PSBzA"

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