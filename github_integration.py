import os
import requests
from flask import current_app
from datetime import datetime

class GitHubIntegration:
    """GitHub integration with full repository management"""
    
    def __init__(self):
        self.hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
        self.x_replit_token = (
            'repl ' + os.environ.get('REPL_IDENTITY') if os.environ.get('REPL_IDENTITY')
            else 'depl ' + os.environ.get('WEB_REPL_RENEWAL') if os.environ.get('WEB_REPL_RENEWAL')
            else None
        )
        self.connection_settings = None
    
    def get_access_token(self):
        """Get fresh access token from Replit connectors"""
        try:
            if self.connection_settings and self.connection_settings.get('settings', {}).get('expires_at'):
                expires_at = datetime.fromisoformat(self.connection_settings['settings']['expires_at'].replace('Z', '+00:00'))
                if expires_at.timestamp() * 1000 > datetime.now().timestamp() * 1000:
                    return self.connection_settings['settings']['access_token']
            
            if not self.x_replit_token:
                raise Exception('X_REPLIT_TOKEN not found for repl/depl')
            
            response = requests.get(
                f'https://{self.hostname}/api/v2/connection?include_secrets=true&connector_names=github',
                headers={
                    'Accept': 'application/json',
                    'X_REPLIT_TOKEN': self.x_replit_token
                }
            )
            response.raise_for_status()
            data = response.json()
            self.connection_settings = data.get('items', [{}])[0] if data.get('items') else {}
            
            access_token = self.connection_settings.get('settings', {}).get('access_token')
            if not access_token:
                raise Exception('GitHub not connected or access token not available')
            
            return access_token
        except Exception as e:
            current_app.logger.error(f"GitHub token error: {e}")
            return None
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make authenticated request to GitHub API"""
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'GitHub not connected'}
        
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {access_token}'
        headers['Accept'] = 'application/vnd.github+json'
        headers['X-GitHub-Api-Version'] = '2022-11-28'
        
        url = f'https://api.github.com/{endpoint}'
        response = requests.request(method, url, headers=headers, **kwargs)
        
        try:
            return response.json()
        except:
            return {'success': True} if response.ok else {'error': response.text}
    
    def get_user(self):
        """Get authenticated user information"""
        return self._make_request('GET', 'user')
    
    def list_repositories(self, sort='updated', per_page=100):
        """List user repositories"""
        return self._make_request('GET', f'user/repos?sort={sort}&per_page={per_page}')
    
    def get_repository(self, owner, repo):
        """Get specific repository details"""
        return self._make_request('GET', f'repos/{owner}/{repo}')
    
    def create_repository(self, name, description='', private=False, auto_init=True):
        """Create a new repository"""
        data = {
            'name': name,
            'description': description,
            'private': private,
            'auto_init': auto_init
        }
        return self._make_request('POST', 'user/repos', json=data)
    
    def delete_repository(self, owner, repo):
        """Delete a repository"""
        return self._make_request('DELETE', f'repos/{owner}/{repo}')
    
    def update_repository(self, owner, repo, **kwargs):
        """Update repository settings"""
        data = {}
        allowed_fields = ['name', 'description', 'homepage', 'private', 'has_issues', 
                         'has_projects', 'has_wiki', 'default_branch']
        
        for field in allowed_fields:
            if field in kwargs:
                data[field] = kwargs[field]
        
        return self._make_request('PATCH', f'repos/{owner}/{repo}', json=data)
    
    def list_branches(self, owner, repo):
        """List repository branches"""
        return self._make_request('GET', f'repos/{owner}/{repo}/branches')
    
    def create_branch(self, owner, repo, branch_name, from_branch='main'):
        """Create a new branch"""
        ref_data = self._make_request('GET', f'repos/{owner}/{repo}/git/ref/heads/{from_branch}')
        
        if 'error' in ref_data or 'object' not in ref_data:
            return {'error': 'Could not get reference branch'}
        
        sha = ref_data['object']['sha']
        data = {
            'ref': f'refs/heads/{branch_name}',
            'sha': sha
        }
        return self._make_request('POST', f'repos/{owner}/{repo}/git/refs', json=data)
    
    def delete_branch(self, owner, repo, branch_name):
        """Delete a branch"""
        return self._make_request('DELETE', f'repos/{owner}/{repo}/git/refs/heads/{branch_name}')
    
    def list_issues(self, owner, repo, state='open', per_page=30):
        """List repository issues"""
        return self._make_request('GET', f'repos/{owner}/{repo}/issues?state={state}&per_page={per_page}')
    
    def create_issue(self, owner, repo, title, body='', labels=None):
        """Create a new issue"""
        data = {
            'title': title,
            'body': body
        }
        if labels:
            data['labels'] = labels
        
        return self._make_request('POST', f'repos/{owner}/{repo}/issues', json=data)
    
    def list_commits(self, owner, repo, per_page=30):
        """List repository commits"""
        return self._make_request('GET', f'repos/{owner}/{repo}/commits?per_page={per_page}')
    
    def get_file_contents(self, owner, repo, path, ref='main'):
        """Get file contents from repository"""
        return self._make_request('GET', f'repos/{owner}/{repo}/contents/{path}?ref={ref}')
    
    def create_or_update_file(self, owner, repo, path, message, content, branch='main', sha=None):
        """Create or update a file in repository"""
        import base64
        data = {
            'message': message,
            'content': base64.b64encode(content.encode()).decode(),
            'branch': branch
        }
        if sha:
            data['sha'] = sha
        
        return self._make_request('PUT', f'repos/{owner}/{repo}/contents/{path}', json=data)
    
    def delete_file(self, owner, repo, path, message, sha, branch='main'):
        """Delete a file from repository"""
        data = {
            'message': message,
            'sha': sha,
            'branch': branch
        }
        return self._make_request('DELETE', f'repos/{owner}/{repo}/contents/{path}', json=data)

def get_github_integration():
    """Get GitHub integration instance"""
    return GitHubIntegration()
