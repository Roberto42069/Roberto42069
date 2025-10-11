import os
import requests
from flask import current_app
from datetime import datetime

class YouTubeIntegration:
    """YouTube integration with full channel management"""
    
    def __init__(self):
        self.hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
        repl_id = os.environ.get('REPL_IDENTITY')
        web_renewal = os.environ.get('WEB_REPL_RENEWAL')
        self.x_replit_token = (
            'repl ' + repl_id if repl_id
            else 'depl ' + web_renewal if web_renewal
            else None
        )
        self.connection_settings = None
        print("📺 YouTube Integration initialized")
    
    def get_access_token(self):
        """Get fresh access token from Replit connectors"""
        try:
            # Check cached token first
            if self.connection_settings and self.connection_settings.get('settings', {}).get('expires_at'):
                try:
                    expires_at = datetime.fromisoformat(self.connection_settings['settings']['expires_at'].replace('Z', '+00:00'))
                    if expires_at.timestamp() > datetime.now().timestamp():
                        print("✅ YouTube: Using cached access token")
                        return self.connection_settings['settings']['access_token']
                except:
                    pass
            
            # Check for required environment variables
            if not self.hostname:
                print("❌ YouTube: REPLIT_CONNECTORS_HOSTNAME not found")
                print("🔐 Please set up YouTube OAuth in Replit Secrets")
                return None
                
            if not self.x_replit_token:
                print("❌ YouTube: X_REPLIT_TOKEN not found")
                print("🔐 Please ensure REPL_IDENTITY or WEB_REPL_RENEWAL is set")
                return None
            
            # Fetch connection settings
            response = requests.get(
                f'https://{self.hostname}/api/v2/connection?include_secrets=true&connector_names=youtube',
                headers={
                    'Accept': 'application/json',
                    'X_REPLIT_TOKEN': self.x_replit_token
                },
                timeout=10
            )
            
            if response.status_code == 401:
                print("❌ YouTube: Not authorized - OAuth connection required")
                print("🔐 To fix: Open Replit Tools → Connections → YouTube → Click 'Connect'")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                self.connection_settings = data[0]
                access_token = self.connection_settings.get('settings', {}).get('access_token')
                if access_token:
                    print("✅ YouTube: Access token refreshed successfully")
                    return access_token
                else:
                    print("❌ YouTube: No access token in connection settings")
                    print("🔐 Please authorize YouTube in Replit Tools → Connections")
                    return None
            else:
                print("❌ YouTube: No connection found - OAuth not completed")
                print("🔐 To fix: Open Replit Tools → Connections → YouTube → Click 'Connect'")
                return None
        except requests.exceptions.Timeout:
            print("❌ YouTube: Connection timeout")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ YouTube integration error: {e}")
            return None
        except Exception as e:
            print(f"❌ YouTube unexpected error: {e}")
            return None
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make authenticated request to YouTube API"""
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'YouTube not connected'}
        
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {access_token}'
        
        url = f'https://www.googleapis.com/youtube/v3/{endpoint}'
        response = requests.request(method, url, headers=headers, **kwargs)
        
        try:
            return response.json()
        except:
            return {'success': True} if response.ok else {'error': response.text}
    
    def get_channel_info(self):
        """Get user's channel information"""
        return self._make_request('GET', 'channels?part=snippet,contentDetails,statistics&mine=true')
    
    def list_videos(self, max_results=50):
        """List user's uploaded videos"""
        channel = self.get_channel_info()
        if 'error' in channel or 'items' not in channel or not channel['items']:
            return {'error': 'Could not get channel information'}
        
        uploads_playlist_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        return self._make_request('GET', f'playlistItems?part=snippet,contentDetails&playlistId={uploads_playlist_id}&maxResults={max_results}')
    
    def get_video_details(self, video_id):
        """Get detailed information about a video"""
        return self._make_request('GET', f'videos?part=snippet,contentDetails,statistics,status&id={video_id}')
    
    def update_video(self, video_id, title=None, description=None, tags=None, category_id=None):
        """Update video metadata"""
        video_data = self.get_video_details(video_id)
        if 'error' in video_data or 'items' not in video_data or not video_data['items']:
            return {'error': 'Could not get video details'}
        
        video_info = video_data['items'][0]
        
        data = {
            'id': video_id,
            'snippet': video_info['snippet']
        }
        
        if title:
            data['snippet']['title'] = title
        if description is not None:
            data['snippet']['description'] = description
        if tags:
            data['snippet']['tags'] = tags
        if category_id:
            data['snippet']['categoryId'] = category_id
        
        return self._make_request('PUT', 'videos?part=snippet', json=data)
    
    def delete_video(self, video_id):
        """Delete a video"""
        return self._make_request('DELETE', f'videos?id={video_id}')
    
    def list_playlists(self, max_results=50):
        """List user's playlists"""
        return self._make_request('GET', f'playlists?part=snippet,contentDetails&mine=true&maxResults={max_results}')
    
    def create_playlist(self, title, description='', privacy_status='private'):
        """Create a new playlist"""
        data = {
            'snippet': {
                'title': title,
                'description': description
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }
        return self._make_request('POST', 'playlists?part=snippet,status', json=data)
    
    def update_playlist(self, playlist_id, title=None, description=None, privacy_status=None):
        """Update playlist details"""
        playlist_data = self._make_request('GET', f'playlists?part=snippet,status&id={playlist_id}')
        if 'error' in playlist_data or 'items' not in playlist_data or not playlist_data['items']:
            return {'error': 'Could not get playlist details'}
        
        playlist_info = playlist_data['items'][0]
        
        data = {
            'id': playlist_id,
            'snippet': playlist_info['snippet'],
            'status': playlist_info['status']
        }
        
        if title:
            data['snippet']['title'] = title
        if description is not None:
            data['snippet']['description'] = description
        if privacy_status:
            data['status']['privacyStatus'] = privacy_status
        
        return self._make_request('PUT', 'playlists?part=snippet,status', json=data)
    
    def delete_playlist(self, playlist_id):
        """Delete a playlist"""
        return self._make_request('DELETE', f'playlists?id={playlist_id}')
    
    def get_playlist_items(self, playlist_id, max_results=50):
        """Get videos in a playlist"""
        return self._make_request('GET', f'playlistItems?part=snippet,contentDetails&playlistId={playlist_id}&maxResults={max_results}')
    
    def add_video_to_playlist(self, playlist_id, video_id):
        """Add a video to a playlist"""
        data = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
        return self._make_request('POST', 'playlistItems?part=snippet', json=data)
    
    def remove_video_from_playlist(self, playlist_item_id):
        """Remove a video from a playlist"""
        return self._make_request('DELETE', f'playlistItems?id={playlist_item_id}')
    
    def search_videos(self, query, max_results=25):
        """Search for videos"""
        return self._make_request('GET', f'search?part=snippet&q={query}&type=video&maxResults={max_results}')
    
    def get_channel_statistics(self):
        """Get channel statistics"""
        channel = self.get_channel_info()
        if 'error' in channel or 'items' not in channel or not channel['items']:
            return {'error': 'Could not get channel information'}
        
        return channel['items'][0].get('statistics', {})
    
    def get_video_comments(self, video_id, max_results=100):
        """Get comments on a video"""
        return self._make_request('GET', f'commentThreads?part=snippet&videoId={video_id}&maxResults={max_results}')

def get_youtube_integration():
    """Get YouTube integration instance"""
    return YouTubeIntegration()
