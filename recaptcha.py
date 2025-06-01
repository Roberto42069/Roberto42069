import os
import requests
from flask import request, current_app

def verify_recaptcha(recaptcha_response):
    """
    Verify reCAPTCHA response with Google's servers
    Returns True if verification is successful, False otherwise
    """
    if not recaptcha_response:
        current_app.logger.warning("No reCAPTCHA response provided")
        return False
    
    secret_key = os.environ.get('RECAPTCHA_SECRET_KEY')
    if not secret_key:
        current_app.logger.error("RECAPTCHA_SECRET_KEY not found in environment variables")
        return False
    
    # Prepare the verification request
    verification_url = 'https://www.google.com/recaptcha/api/siteverify'
    payload = {
        'secret': secret_key,
        'response': recaptcha_response,
        'remoteip': request.environ.get('REMOTE_ADDR')
    }
    
    try:
        # Make the verification request
        current_app.logger.info(f"Making reCAPTCHA verification request to Google")
        response = requests.post(verification_url, data=payload, timeout=10)
        result = response.json()
        
        current_app.logger.info(f"reCAPTCHA verification response: {result}")
        
        # Check if verification was successful
        if result.get('success'):
            current_app.logger.info("reCAPTCHA verification successful")
            return True
        else:
            error_codes = result.get('error-codes', [])
            current_app.logger.warning(f"reCAPTCHA verification failed with error codes: {error_codes}")
            
            # Provide helpful error messages
            if 'invalid-input-secret' in error_codes:
                current_app.logger.error("Invalid reCAPTCHA secret key")
            elif 'missing-input-response' in error_codes:
                current_app.logger.error("Missing reCAPTCHA response")
            elif 'invalid-input-response' in error_codes:
                current_app.logger.error("Invalid reCAPTCHA response")
            elif 'timeout-or-duplicate' in error_codes:
                current_app.logger.error("reCAPTCHA response timeout or duplicate")
                
            return False
            
    except requests.RequestException as e:
        current_app.logger.error(f"reCAPTCHA verification request failed: {e}")
        return False
    except Exception as e:
        current_app.logger.error(f"Unexpected error during reCAPTCHA verification: {e}")
        return False

def is_recaptcha_enabled():
    """Check if reCAPTCHA is properly configured"""
    site_key = os.environ.get('RECAPTCHA_SITE_KEY')
    secret_key = os.environ.get('RECAPTCHA_SECRET_KEY')
    return bool(site_key and secret_key)