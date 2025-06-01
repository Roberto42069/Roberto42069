#!/usr/bin/env python3

import os
import requests

def test_recaptcha_keys():
    """Test if RECAPTCHA keys are properly configured"""
    
    site_key = os.environ.get('RECAPTCHA_SITE_KEY')
    secret_key = os.environ.get('RECAPTCHA_SECRET_KEY')
    
    print("=== RECAPTCHA Configuration Test ===")
    print(f"Site Key present: {'Yes' if site_key else 'No'}")
    print(f"Secret Key present: {'Yes' if secret_key else 'No'}")
    
    if site_key:
        print(f"Site Key (first 10 chars): {site_key[:10]}...")
    if secret_key:
        print(f"Secret Key (first 10 chars): {secret_key[:10]}...")
    
    # Test with a dummy response to see what error we get
    if secret_key:
        print("\n=== Testing Secret Key Validity ===")
        verification_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': secret_key,
            'response': 'dummy_response_for_testing',
            'remoteip': '127.0.0.1'
        }
        
        try:
            response = requests.post(verification_url, data=payload, timeout=10)
            result = response.json()
            print(f"Google's response: {result}")
            
            if 'invalid-input-secret' in result.get('error-codes', []):
                print("❌ ERROR: Invalid secret key - please check your RECAPTCHA_SECRET_KEY")
            elif 'invalid-input-response' in result.get('error-codes', []):
                print("✓ Secret key is valid (got expected 'invalid-input-response' for dummy data)")
            else:
                print(f"Unexpected response: {result}")
                
        except Exception as e:
            print(f"❌ Error testing secret key: {e}")

if __name__ == "__main__":
    test_recaptcha_keys()