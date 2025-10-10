import os
import json
import requests
from datetime import datetime, timedelta
from flask import current_app

class SpotifyIntegration:
    """Spotify integration with full read/write access"""
    
    def __init__(self):
        self.hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
        self.x_replit_token = (
            'repl ' + os.environ.get('REPL_IDENTITY') if os.environ.get('REPL_IDENTITY')
            else 'depl ' + os.environ.get('WEB_REPL_RENEWAL') if os.environ.get('WEB_REPL_RENEWAL')
            else None
        )
        self.connection_settings = None
        print("🎵 Spotify Integration initialized")
    
    def get_access_token(self):
        """Get fresh access token from Replit connectors"""
        try:
            if self.connection_settings and self.connection_settings.get('settings', {}).get('expires_at'):
                expires_at = datetime.fromisoformat(self.connection_settings['settings']['expires_at'].replace('Z', '+00:00'))
                if expires_at.timestamp() * 1000 > datetime.now().timestamp() * 1000:
                    print("✅ Spotify: Using cached access token")
                    return self.connection_settings['settings']['access_token']
            
            if not self.x_replit_token:
                print("❌ Spotify: X_REPLIT_TOKEN not found")
                raise Exception('X_REPLIT_TOKEN not found for repl/depl')
            
            response = requests.get(
                f'https://{self.hostname}/api/v2/connection?include_secrets=true&connector_names=spotify',
                headers={
                    'Accept': 'application/json',
                    'X_REPLIT_TOKEN': self.x_replit_token
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                self.connection_settings = data[0]
                print("✅ Spotify: Access token refreshed successfully")
                return self.connection_settings['settings']['access_token']
            else:
                print("❌ Spotify: No connection settings found")
                return None
        except Exception as e:
            print(f"❌ Spotify integration error: {e}")
            return None
            self.connection_settings = data.get('items', [{}])[0] if data.get('items') else {}
            
            access_token = self.connection_settings.get('settings', {}).get('access_token')
            if not access_token:
                raise Exception('Spotify not connected or access token not available')
            
            return access_token
        except Exception as e:
            current_app.logger.error(f"Spotify token error: {e}")
            return None
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make authenticated request to Spotify API"""
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Spotify not connected'}
        
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {access_token}'
        
        url = f'https://api.spotify.com/v1/{endpoint}'
        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 204:
            return {'success': True}
        
        try:
            return response.json()
        except:
            return {'success': True} if response.ok else {'error': response.text}
    
    def get_current_playback(self):
        """Get currently playing track"""
        return self._make_request('GET', 'me/player/currently-playing')
    
    def get_recently_played(self, limit=50):
        """Get recently played tracks"""
        return self._make_request('GET', f'me/player/recently-played?limit={limit}')
    
    def get_user_profile(self):
        """Get user profile information"""
        return self._make_request('GET', 'me')
    
    def get_user_playlists(self, limit=50):
        """Get user's playlists"""
        return self._make_request('GET', f'me/playlists?limit={limit}')
    
    def create_playlist(self, name, description='', public=True):
        """Create a new playlist"""
        profile = self.get_user_profile()
        if 'error' in profile or 'id' not in profile:
            return {'error': 'Could not get user profile'}
        
        user_id = profile['id']
        data = {
            'name': name,
            'description': description,
            'public': public
        }
        return self._make_request('POST', f'users/{user_id}/playlists', json=data)
    
    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """Add tracks to a playlist"""
        data = {'uris': track_uris}
        return self._make_request('POST', f'playlists/{playlist_id}/tracks', json=data)
    
    def remove_tracks_from_playlist(self, playlist_id, track_uris):
        """Remove tracks from a playlist"""
        data = {'tracks': [{'uri': uri} for uri in track_uris]}
        return self._make_request('DELETE', f'playlists/{playlist_id}/tracks', json=data)
    
    def update_playlist_details(self, playlist_id, name=None, description=None, public=None):
        """Update playlist details"""
        data = {}
        if name:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if public is not None:
            data['public'] = public
        
        return self._make_request('PUT', f'playlists/{playlist_id}', json=data)
    
    def get_playlist_tracks(self, playlist_id, limit=100):
        """Get tracks from a playlist"""
        return self._make_request('GET', f'playlists/{playlist_id}/tracks?limit={limit}')
    
    def play(self, context_uri=None, uris=None, position_ms=0):
        """Start/resume playback"""
        data = {}
        if context_uri:
            data['context_uri'] = context_uri
        if uris:
            data['uris'] = uris
        if position_ms:
            data['position_ms'] = position_ms
        
        return self._make_request('PUT', 'me/player/play', json=data if data else None)
    
    def pause(self):
        """Pause playback"""
        return self._make_request('PUT', 'me/player/pause')
    
    def skip_to_next(self):
        """Skip to next track"""
        return self._make_request('POST', 'me/player/next')
    
    def skip_to_previous(self):
        """Skip to previous track"""
        return self._make_request('POST', 'me/player/previous')
    
    def set_volume(self, volume_percent):
        """Set playback volume (0-100)"""
        return self._make_request('PUT', f'me/player/volume?volume_percent={volume_percent}')
    
    def search(self, query, search_type='track', limit=20):
        """Search for tracks, artists, albums, or playlists"""
        return self._make_request('GET', f'search?q={query}&type={search_type}&limit={limit}')
    
    def get_top_tracks(self, time_range='medium_term', limit=50):
        """Get user's top tracks"""
        return self._make_request('GET', f'me/top/tracks?time_range={time_range}&limit={limit}')
    
    def get_top_artists(self, time_range='medium_term', limit=50):
        """Get user's top artists"""
        return self._make_request('GET', f'me/top/artists?time_range={time_range}&limit={limit}')
    
    def add_to_queue(self, track_uri):
        """Add a track to the queue"""
        return self._make_request('POST', f'me/player/queue?uri={track_uri}')

def get_spotify_integration():
    """Get Spotify integration instance"""
    return SpotifyIntegration()
