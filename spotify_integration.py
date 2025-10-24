import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Load Spotify API credentials from environment variables or a secure config file
# (Do not hardcode these in production!)
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')
SPOTIFY_SCOPE = 'user-library-read playlist-modify-public user-read-playback-state user-modify-playback-state'

# Initialize Spotify OAuth
sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URI, scope=SPOTIFY_SCOPE)

# Function to get or refresh access token
def get_spotify_token():
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        print(f"Please visit this URL to authorize: {auth_url}")
        # In a real app, handle the redirect and code exchange here
        # For simplicity, assume manual input or web flow
        response = input("Enter the URL you were redirected to: ")
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)
    return token_info['access_token']

# Main Spotify client initializer
def init_spotify_client():
    token = get_spotify_token()
    return spotipy.Spotify(auth=token)

# Function to recommend tracks based on cultural context
# Integrates with cultural_heritage_viz.py's context