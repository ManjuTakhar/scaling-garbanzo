#!/usr/bin/env python3
"""
Magic Link Authentication Test Script

This script tests the complete magic link authentication flow:
1. Send magic link for login
2. Verify magic link token
3. Authenticate user and get JWT
4. Test token validation

Usage:
    python test_magic_link.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if running on different port
TEST_EMAIL = "test@example.com"

def test_magic_link_flow():
    """Test the complete magic link authentication flow"""
    
    print("🧪 Testing Magic Link Authentication Flow")
    print("=" * 50)
    
    # Step 1: Send magic link
    print("\n1️⃣ Sending magic link...")
    send_response = send_magic_link()
    
    if send_response["success"]:
        print(f"✅ Magic link sent successfully")
        print(f"   Token ID: {send_response['data']['token_id']}")
        print(f"   Expires at: {datetime.fromtimestamp(send_response['data']['expires_at'])}")
        
        # Extract token from the response (in real scenario, this would be in email)
        # For testing, we'll need to get the actual token from the database or email
        token = send_response.get("token")  # This would be extracted from email in real scenario
        
        if token:
            # Step 2: Check token status
            print("\n2️⃣ Checking token status...")
            status_response = check_token_status(token)
            
            if status_response["success"]:
                print(f"✅ Token is valid")
                print(f"   Email: {status_response['data']['email']}")
                print(f"   Purpose: {status_response['data']['purpose']}")
                
                # Step 3: Verify and authenticate
                print("\n3️⃣ Verifying and authenticating...")
                auth_response = verify_and_authenticate(token)
                
                if auth_response["success"]:
                    print(f"✅ Authentication successful")
                    print(f"   User ID: {auth_response['data']['user']['user_id']}")
                    print(f"   Access Token: {auth_response['data']['access_token'][:20]}...")
                    
                    # Step 4: Test token validation
                    print("\n4️⃣ Testing token validation...")
                    validate_response = test_token_validation(auth_response['data']['access_token'])
                    
                    if validate_response["success"]:
                        print(f"✅ Token validation successful")
                        print(f"   User: {validate_response['data']['name']} ({validate_response['data']['email']})")
                    else:
                        print(f"❌ Token validation failed: {validate_response['error']}")
                else:
                    print(f"❌ Authentication failed: {auth_response['error']}")
            else:
                print(f"❌ Token status check failed: {status_response['error']}")
        else:
            print("⚠️ No token available for testing (would be extracted from email)")
    else:
        print(f"❌ Failed to send magic link: {send_response['error']}")
    
    print("\n" + "=" * 50)
    print("🏁 Magic Link Flow Test Complete")


def send_magic_link():
    """Send a magic link for login"""
    url = f"{BASE_URL}/api/auth/magic/send"
    data = {
        "email": TEST_EMAIL,
        "purpose": "login"
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


def check_token_status(token):
    """Check the status of a magic link token"""
    url = f"{BASE_URL}/api/auth/magic/status/{token}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


def verify_and_authenticate(token):
    """Verify magic link and authenticate user"""
    url = f"{BASE_URL}/api/auth/magic/authenticate"
    params = {"token": token}
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


def test_token_validation(access_token):
    """Test token validation by calling a protected endpoint"""
    url = f"{BASE_URL}/api/users/initialize"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


def test_cleanup():
    """Test cleanup of expired magic links"""
    url = f"{BASE_URL}/api/auth/magic/cleanup"
    
    try:
        response = requests.delete(url)
        response.raise_for_status()
        
        result = response.json()
        print(f"🧹 Cleanup completed: {result['message']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Cleanup failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Magic Link Authentication Tests")
    print(f"📧 Test Email: {TEST_EMAIL}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    # Test the main flow
    test_magic_link_flow()
    
    # Test cleanup
    print("\n🧹 Testing cleanup...")
    test_cleanup()
    
    print("\n✨ All tests completed!")
















