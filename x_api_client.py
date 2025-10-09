"""
🚀 X API (Grok) Integration for Roboto SAI
Integrates X's Grok AI as the main AI provider with bearer token authentication
"""

import os
import requests
import json
from typing import List, Dict, Any, Optional

class XAPIClient:
    """X API (Grok) client with bearer token authentication"""
    
    def __init__(self, silent=True):
        self.api_token = os.environ.get("X_API_TOKEN")
        self.api_secret = os.environ.get("X_API_SECRET")
        self.silent = silent  # Control verbose output
        
        # X AI (Grok) endpoint - using the proper Grok API endpoint
        self.base_url = "https://api.x.ai/v1"
        
        # Validate API key format - X API keys should NOT start with 'GK' or other invalid patterns
        self.valid_key = self._validate_key_format(self.api_token)
        
        # Setup headers with bearer token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Only mark as available if we have a key AND it's valid format
        self.available = bool(self.api_token) and self.valid_key
        
        # Suppress verbose output unless explicitly needed
        if not self.silent:
            if self.available:
                print(f"🐦 X API (Grok) initialized with bearer token authentication")
            elif self.api_token and not self.valid_key:
                print("⚠️ X API key format appears invalid. Using fallback AI provider.")
            else:
                print("⚠️ X API credentials not found. Using fallback AI provider.")
    
    def _validate_key_format(self, key: Optional[str]) -> bool:
        """
        Validate X API key format
        
        Returns False if:
        - Key is None or empty
        - Key starts with 'GK' (invalid OpenAI format)
        - Key has other known invalid patterns
        """
        if not key:
            return False
        
        # Check for known invalid patterns
        invalid_prefixes = ['GK', 'sk-', 'pk-']  # Common OpenAI/other API key prefixes
        
        for prefix in invalid_prefixes:
            if key.startswith(prefix):
                return False
        
        # X API keys should start with 'xai-'
        if key.startswith('xai-'):
            return True
        
        # Accept other formats but not the known invalid ones
        return True
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "grok-2-1212",  # Updated to use current model
        max_tokens: int = 300,
        temperature: float = 0.8,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion using X's Grok AI
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Grok model to use (default: grok-beta)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Response dictionary with AI completion
        """
        if not self.available:
            raise Exception("X API client not properly initialized - missing credentials")
        
        # Prepare request payload
        payload = {
            "messages": messages,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        # Add any additional parameters
        payload.update(kwargs)
        
        try:
            # Make API request to Grok
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"X API error: {response.status_code} - {response.text}"
                if not self.silent:
                    print(error_msg)
                raise Exception(error_msg)
            
            # Parse response
            result = response.json()
            
            # Format response to match OpenAI structure for compatibility
            formatted_response = {
                "choices": [{
                    "message": {
                        "content": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                        "role": "assistant"
                    },
                    "finish_reason": result.get("choices", [{}])[0].get("finish_reason", "stop")
                }],
                "usage": result.get("usage", {}),
                "model": result.get("model", model)
            }
            
            return formatted_response
            
        except requests.exceptions.RequestException as e:
            error_msg = f"X API request failed: {str(e)}"
            if not self.silent:
                print(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"X API error: {str(e)}"
            if not self.silent:
                print(error_msg)
            raise Exception(error_msg)

    def test_connection(self, timeout: int = 5) -> bool:
        """Test X API connection with short timeout to prevent worker hangs"""
        if not self.available:
            return False
        
        try:
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
            
            # Use shorter timeout for test to prevent initialization hangs
            payload = {
                "messages": test_messages,
                "model": "grok-2-1212",
                "max_tokens": 10,
                "temperature": 0.8,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=timeout  # Short timeout for test
            )
            
            if response.status_code == 200:
                result = response.json()
                return bool(result.get("choices", [{}])[0].get("message", {}).get("content"))
            
            return False
            
        except requests.exceptions.Timeout:
            if not self.silent:
                print(f"⚠️ X API connection test timed out after {timeout}s - API may be slow")
            return False
        except Exception as e:
            # Suppress verbose output unless explicitly needed
            if not self.silent:
                if "Incorrect API key" in str(e) or "invalid argument" in str(e):
                    print(f"⚠️ X API key invalid - please get a valid key from https://console.x.ai")
                else:
                    print(f"X API connection test failed: {e}")
            return False


def get_x_api_client(silent=True):
    """Factory function to get X API client"""
    return XAPIClient(silent=silent)


# Test the client when run directly
if __name__ == "__main__":
    client = XAPIClient()
    
    if client.available:
        print("\n🐦 Testing X API (Grok) connection...")
        if client.test_connection():
            print("✅ X API (Grok) connection successful!")
        else:
            print("❌ X API (Grok) connection failed")
    else:
        print("❌ X API credentials not configured")
