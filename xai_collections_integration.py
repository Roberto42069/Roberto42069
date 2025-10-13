
"""
xAI Collections Integration for Roboto SAI
Enables enterprise-grade document management and semantic search
Created for Roberto Villarreal Martinez
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

class XAICollectionsManager:
    """
    Manage xAI Collections for Roboto SAI
    Provides document storage, embedding, and semantic search capabilities
    """
    
    def __init__(self):
        self.api_key = os.environ.get("XAI_API_KEY") or os.environ.get("X_API_KEY")
        self.base_url = "https://api.x.ai/v1"
        self.collections = {}
        self.files = {}
        
        if not self.api_key:
            logging.warning("XAI_API_KEY not found. Collections features will be limited.")
    
    def create_collection(self, name: str, description: str = "", auto_embed: bool = True) -> Dict[str, Any]:
        """
        Create a new collection with optional auto-embedding
        
        Args:
            name: Collection name
            description: Collection description
            auto_embed: Whether to automatically generate embeddings for uploaded files
        
        Returns:
            Collection metadata
        """
        if not self.api_key:
            return {"error": "XAI_API_KEY not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": name,
            "description": description,
            "auto_embed": auto_embed,
            "metadata": {
                "created_by": "Roboto SAI",
                "creator": "Roberto Villarreal Martinez",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/collections",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                collection_data = response.json()
                self.collections[collection_data['id']] = collection_data
                logging.info(f"✅ Created collection: {name}")
                return collection_data
            else:
                logging.error(f"Failed to create collection: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logging.error(f"Collection creation error: {e}")
            return {"error": str(e)}
    
    def upload_file(self, collection_id: str, file_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Upload a file to a collection
        
        Args:
            collection_id: Target collection ID
            file_path: Path to file to upload
            metadata: Optional file metadata
        
        Returns:
            File upload result
        """
        if not self.api_key:
            return {"error": "XAI_API_KEY not configured"}
        
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        file_metadata = metadata or {}
        file_metadata.update({
            "uploaded_by": "Roboto SAI",
            "upload_timestamp": datetime.now().isoformat()
        })
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'collection_id': collection_id,
                    'metadata': json.dumps(file_metadata)
                }
                
                response = requests.post(
                    f"{self.base_url}/files",
                    headers=headers,
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                file_data = response.json()
                self.files[file_data['id']] = file_data
                logging.info(f"✅ Uploaded file: {file_path} to collection {collection_id}")
                return file_data
            else:
                logging.error(f"Failed to upload file: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logging.error(f"File upload error: {e}")
            return {"error": str(e)}
    
    def semantic_search(self, query: str, collection_ids: Optional[List[str]] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search across collections
        
        Args:
            query: Search query
            collection_ids: List of collection IDs to search (None = all collections)
            limit: Maximum number of results
        
        Returns:
            List of relevant documents with relevance scores
        """
        if not self.api_key:
            return [{"error": "XAI_API_KEY not configured"}]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "limit": limit
        }
        
        if collection_ids:
            payload["collection_ids"] = collection_ids
        
        try:
            response = requests.post(
                f"{self.base_url}/collections/search",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                results = response.json()
                logging.info(f"🔍 Semantic search returned {len(results.get('results', []))} results")
                return results.get('results', [])
            else:
                logging.error(f"Search failed: {response.text}")
                return [{"error": response.text}]
                
        except Exception as e:
            logging.error(f"Search error: {e}")
            return [{"error": str(e)}]
    
    def add_file_to_collection(self, file_id: str, collection_id: str) -> Dict[str, Any]:
        """
        Add an existing file to another collection
        A file can belong to multiple collections
        
        Args:
            file_id: ID of the file to add
            collection_id: Target collection ID
        
        Returns:
            Operation result
        """
        if not self.api_key:
            return {"error": "XAI_API_KEY not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "file_id": file_id,
            "collection_id": collection_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/collections/{collection_id}/files",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                logging.info(f"✅ Added file {file_id} to collection {collection_id}")
                return response.json()
            else:
                logging.error(f"Failed to add file to collection: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logging.error(f"Add file to collection error: {e}")
            return {"error": str(e)}
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections"""
        if not self.api_key:
            return [{"error": "XAI_API_KEY not configured"}]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/collections",
                headers=headers
            )
            
            if response.status_code == 200:
                collections = response.json()
                return collections.get('collections', [])
            else:
                return [{"error": response.text}]
                
        except Exception as e:
            logging.error(f"List collections error: {e}")
            return [{"error": str(e)}]
    
    def get_collection_files(self, collection_id: str) -> List[Dict[str, Any]]:
        """Get all files in a collection"""
        if not self.api_key:
            return [{"error": "XAI_API_KEY not configured"}]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/collections/{collection_id}/files",
                headers=headers
            )
            
            if response.status_code == 200:
                files = response.json()
                return files.get('files', [])
            else:
                return [{"error": response.text}]
                
        except Exception as e:
            logging.error(f"Get collection files error: {e}")
            return [{"error": str(e)}]
    
    def integrate_with_roboto_memory(self, roboto_instance):
        """
        Integrate Collections with Roboto's memory system
        Upload important memories and enable semantic search
        """
        try:
            # Create a collection for Roboto's memories
            memory_collection = self.create_collection(
                name="Roboto_SAI_Memories",
                description="Roberto Villarreal Martinez's conversations and knowledge base",
                auto_embed=True
            )
            
            if "error" in memory_collection:
                logging.error(f"Failed to create memory collection: {memory_collection['error']}")
                return
            
            collection_id = memory_collection['id']
            
            # Export important memories to files
            if hasattr(roboto_instance, 'memory_system') and roboto_instance.memory_system:
                important_memories = [
                    m for m in roboto_instance.memory_system.episodic_memories
                    if m.get('importance', 0) > 0.7
                ]
                
                # Create a memory export file
                memory_file = "roboto_important_memories.json"
                with open(memory_file, 'w') as f:
                    json.dump(important_memories, f, indent=2)
                
                # Upload to collection
                upload_result = self.upload_file(
                    collection_id=collection_id,
                    file_path=memory_file,
                    metadata={
                        "type": "episodic_memories",
                        "count": len(important_memories),
                        "creator": "Roberto Villarreal Martinez"
                    }
                )
                
                if "error" not in upload_result:
                    logging.info(f"✅ Uploaded {len(important_memories)} important memories to Collections")
                
            return collection_id
            
        except Exception as e:
            logging.error(f"Memory integration error: {e}")
            return None

# Global instance
xai_collections = XAICollectionsManager()

def get_xai_collections():
    """Get the global XAI Collections manager instance"""
    return xai_collections
