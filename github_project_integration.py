
import requests
import json
import os
from datetime import datetime
import logging

class GitHubProjectIntegration:
    """GitHub Projects API integration for Roboto SAI"""
    
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.project_url = "https://github.com/users/Roberto42069/projects/1"
        self.api_base = "https://api.github.com"
        self.headers = {
            'Authorization': f'Bearer {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Roboto-SAI/1.0'
        }
        self.logger = logging.getLogger(__name__)
        
    def get_project_data(self):
        """Fetch project data from GitHub API"""
        try:
            # Get user projects
            response = requests.get(
                f"{self.api_base}/users/Roberto42069/projects",
                headers=self.headers
            )
            
            if response.status_code == 200:
                projects = response.json()
                # Find project with ID 1
                for project in projects:
                    if project['number'] == 1:
                        return project
            else:
                self.logger.warning(f"GitHub API error: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error fetching project data: {e}")
            
        return None
    
    def get_project_items(self):
        """Get all items/cards from the project"""
        try:
            project = self.get_project_data()
            if not project:
                return []
                
            # Get project columns
            columns_response = requests.get(
                f"{self.api_base}/projects/{project['id']}/columns",
                headers=self.headers
            )
            
            if columns_response.status_code != 200:
                return []
                
            columns = columns_response.json()
            all_items = []
            
            for column in columns:
                # Get cards for each column
                cards_response = requests.get(
                    f"{self.api_base}/projects/columns/{column['id']}/cards",
                    headers=self.headers
                )
                
                if cards_response.status_code == 200:
                    cards = cards_response.json()
                    for card in cards:
                        all_items.append({
                            'id': card['id'],
                            'note': card.get('note', ''),
                            'column': column['name'],
                            'created_at': card['created_at'],
                            'updated_at': card['updated_at'],
                            'content_url': card.get('content_url')
                        })
            
            return all_items
            
        except Exception as e:
            self.logger.error(f"Error fetching project items: {e}")
            return []
    
    def create_project_card(self, column_name, note):
        """Create a new card in the specified column"""
        try:
            project = self.get_project_data()
            if not project:
                return None
                
            # Get columns
            columns_response = requests.get(
                f"{self.api_base}/projects/{project['id']}/columns",
                headers=self.headers
            )
            
            if columns_response.status_code != 200:
                return None
                
            columns = columns_response.json()
            target_column = None
            
            for column in columns:
                if column['name'].lower() == column_name.lower():
                    target_column = column
                    break
            
            if not target_column:
                return None
            
            # Create card
            card_data = {
                'note': note
            }
            
            response = requests.post(
                f"{self.api_base}/projects/columns/{target_column['id']}/cards",
                headers=self.headers,
                json=card_data
            )
            
            if response.status_code == 201:
                return response.json()
                
        except Exception as e:
            self.logger.error(f"Error creating project card: {e}")
            
        return None
    
    def get_project_summary(self):
        """Get a summary of the current project status"""
        try:
            items = self.get_project_items()
            if not items:
                return "No project data available"
            
            # Group by column
            columns = {}
            for item in items:
                column = item['column']
                if column not in columns:
                    columns[column] = []
                columns[column].append(item)
            
            summary = f"📋 GitHub Project Status:\n"
            summary += f"🔗 Project: {self.project_url}\n\n"
            
            for column_name, cards in columns.items():
                summary += f"**{column_name}** ({len(cards)} items)\n"
                for card in cards[:3]:  # Show first 3 items
                    note = card['note'][:50] + "..." if len(card['note']) > 50 else card['note']
                    summary += f"  • {note}\n"
                if len(cards) > 3:
                    summary += f"  ... and {len(cards) - 3} more\n"
                summary += "\n"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating project summary: {e}")
            return "Error generating project summary"
    
    def sync_with_roboto_tasks(self, roboto_instance):
        """Sync GitHub project items with Roboto's task system"""
        try:
            items = self.get_project_items()
            synced_tasks = []
            
            for item in items:
                if item['note'].strip():
                    task_data = {
                        'text': item['note'],
                        'status': item['column'],
                        'github_id': item['id'],
                        'created_at': item['created_at'],
                        'updated_at': item['updated_at'],
                        'source': 'github_project'
                    }
                    synced_tasks.append(task_data)
            
            # Store in Roboto's memory system if available
            if hasattr(roboto_instance, 'memory_system') and roboto_instance.memory_system:
                roboto_instance.memory_system.add_episodic_memory(
                    f"GitHub project sync: {len(synced_tasks)} tasks",
                    f"Synchronized {len(synced_tasks)} tasks from GitHub project board",
                    "productivity",
                    "Roberto Villarreal Martinez"
                )
            
            return synced_tasks
            
        except Exception as e:
            self.logger.error(f"Error syncing with Roboto tasks: {e}")
            return []

def get_github_integration():
    """Factory function to get GitHub integration instance"""
    return GitHubProjectIntegration()
