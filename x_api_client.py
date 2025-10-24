"""
🚀 X API (Grok) Integration for Roboto SAI
Integrates X's Grok AI as the main AI provider with bearer token authentication
"""

import os
import requests
import time
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
                print("🐦 X API (Grok) initialized with bearer token authentication")
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
        model: str = "grok-4",  # ✅ Using Grok-4 for advanced reasoning
        max_tokens: int = 8000,
        temperature: float = 0.8,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion using X's Grok AI
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Grok model to use (default: grok-beta)
            max_tokens: Maximum tokens in response (default 8000, expandable to 32k)
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
        
        # Retry logic for transient network issues
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Make API request to Grok with extended timeout for Grok-4 reasoning
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=180  # Increased to 3 minutes for Grok-4's deep reasoning
                )
                
                # Check for errors
                if response.status_code != 200:
                    error_msg = f"X API error: {response.status_code} - {response.text}"
                    if not self.silent:
                        print(error_msg)
                    raise Exception(error_msg)
                
                # Success - break out of retry loop
                break
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    if not self.silent:
                        print(f"⚠️ Grok-4 request timed out (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    raise Exception("X API request timed out after multiple retries - Grok-4 may be under heavy load")
            
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1 and "timeout" in str(e).lower():
                    if not self.silent:
                        print(f"⚠️ Network error (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    error_msg = f"X API request failed: {str(e)}"
                    if not self.silent:
                        print(error_msg)
                    raise Exception(error_msg)
        
        # Parse response after successful request
        try:
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
            
        except Exception as e:
            error_msg = f"X API error parsing response: {str(e)}"
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
                "model": "grok-4",
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
                    print("⚠️ X API key invalid - please get a valid key from https://console.x.ai")
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
